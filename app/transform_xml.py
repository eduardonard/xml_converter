import base64
from typing import Optional, Dict, List

from fastapi import HTTPException
import xml.etree.ElementTree as ET

from app.constants import ROSSUM_CREDENTIALS


def extract_value_from_datapoint(
    item: ET.Element, datapoint: str, fallback_datapoint: Optional[str] = ""
) -> str:
    value = item.findtext(f"datapoint[@schema_id='{datapoint}']")
    if value:
        return value
    return item.findtext(f"datapoint[@schema_id='{fallback_datapoint}']")


def extract_value_from_section_and_datapoint(
    root: ET.Element,
    section: str,
    datapoint: str,
    fallback_section: Optional[str] = None,
    fallback_datapoint: Optional[str] = None,
) -> str:

    def find_value(section_id: str, datapoint_id: str) -> Optional[str]:
        path = f'.//section[@schema_id="{section_id}"]/datapoint[@schema_id="{datapoint_id}"]'
        return root.findtext(path)

    # Try primary section and datapoint
    value = find_value(section, datapoint)

    # Try fallback section and datapoint if provided
    if not value and fallback_section and fallback_datapoint:
        value = find_value(fallback_section, fallback_datapoint)

    return value or ""


def add_sub_element(parent: ET.Element, tag: str, text: str = "") -> ET.Element:
    """
    Helper function to add a sub-element with text to a parent XML element.
    """
    element = ET.SubElement(parent, tag)
    element.text = text
    return element


def extract_invoice_data(root: ET.Element) -> Dict[str, str]:
    """
    Extracts invoice data from the XML root element and returns it as a dictionary.
    """
    data = {
        "document_id": extract_value_from_section_and_datapoint(
            root, "basic_info_section", "document_id"
        ),
        "invoice_date": extract_value_from_section_and_datapoint(
            root, "basic_info_section", "date_issue"
        ),
        "invoice_due": extract_value_from_section_and_datapoint(
            root, "basic_info_section", "date_due"
        ),
        "total_amount": extract_value_from_section_and_datapoint(
            root, "amounts_section", "amount_total"
        ),
        "iban": extract_value_from_section_and_datapoint(
            root, "payment_info_section", "iban"
        ),
        "currency": extract_value_from_section_and_datapoint(
            root, "amounts_section", "currency", "totals_section", "currency"
        ),
        "vendor": extract_value_from_section_and_datapoint(
            root, "vendor_section", "sender_name"
        ),
        "vendor_address": extract_value_from_section_and_datapoint(
            root, "vendor_section", "sender_address"
        ),
        "amount_due": extract_value_from_section_and_datapoint(
            root, "amounts_section", "amount_due", "totals_section", "amount_due"
        ),
        "notes": extract_value_from_section_and_datapoint(
            root, "others_section", "notes"
        ),
    }
    data["invoice_date"] = f"{data['invoice_date']}T00:00:00"
    data["invoice_due"] = f"{data['invoice_due']}T00:00:00"

    # Calculate total amount if not directly available
    if not data["total_amount"]:
        base = extract_value_from_section_and_datapoint(
            root, "totals_section", "amount_total_base"
        )
        tax = extract_value_from_section_and_datapoint(
            root, "totals_section", "amount_total_tax"
        )
        data["total_amount"] = str(float(base) + float(tax)) if base and tax else ""

    data["line_items"] = extract_line_items(root)

    return data


def extract_line_items(root: ET.Element) -> List[Dict[str, str]]:
    """
    Extracts line items from the XML root element and returns them as a list of dictionaries.
    """
    line_items = []
    for item in root.findall(
        './/section[@schema_id="line_items_section"]/multivalue/tuple'
    ):
        line_item = {
            "item_amount": extract_value_from_datapoint(
                item, "item_total_base", "item_amount_total"
            ),
            "item_quantity": extract_value_from_datapoint(item, "item_quantity"),
            "item_description": extract_value_from_datapoint(item, "item_description"),
            "account_id": extract_value_from_datapoint(item, "account_id"),
        }
        line_items.append(line_item)
    return line_items


def build_invoice_xml(data: Dict[str, str]) -> str:
    """
    Builds an XML structure for the invoice from the extracted data dictionary.
    """
    # Create the root for the new XML structure
    invoice_registers = ET.Element("InvoiceRegisters")
    invoices = ET.SubElement(invoice_registers, "Invoices")
    payable = ET.SubElement(invoices, "Payable")

    # Populate the new XML structure
    add_sub_element(payable, "InvoiceNumber", data["document_id"])
    add_sub_element(payable, "InvoiceDate", data["invoice_date"])
    add_sub_element(payable, "DueDate", data["invoice_due"])
    add_sub_element(payable, "TotalAmount", data["total_amount"])
    add_sub_element(payable, "Notes", data["notes"])
    add_sub_element(payable, "Iban", data["iban"])
    add_sub_element(payable, "Amount", data["amount_due"])
    add_sub_element(payable, "Currency", data["currency"])
    add_sub_element(payable, "Vendor", data["vendor"])
    add_sub_element(payable, "VendorAddress", data["vendor_address"])

    details_element = ET.SubElement(payable, "Details")

    # Process line items
    for item in data["line_items"]:
        detail_element = ET.SubElement(details_element, "Detail")
        add_sub_element(detail_element, "Amount", item["item_amount"])
        add_sub_element(detail_element, "AccountId", item["account_id"])
        add_sub_element(detail_element, "Quantity", item["item_quantity"])
        add_sub_element(detail_element, "Notes", item["item_description"])

    # Convert the new XML structure to a string
    transformed_xml = ET.tostring(
        invoice_registers, encoding="utf-8", method="xml"
    ).decode("utf-8")

    return transformed_xml


def transform_invoice_xml(input_xml: str) -> str:
    """
    Transforms the input invoice XML into the desired output XML format.
    """
    root = ET.fromstring(input_xml)

    # Extract data into a dictionary
    data = extract_invoice_data(root)

    # Build and return the transformed XML
    return build_invoice_xml(data)


def xml_to_base64(xml_data: str) -> str:
    xml_bytes = xml_data.encode("utf-8")
    base64_bytes = base64.b64encode(xml_bytes)
    base64_string = base64_bytes.decode("utf-8")

    return base64_string


def filter_xml_by_annotation_id(xml_str: str, annotation_id: int) -> str:
    root = ET.fromstring(xml_str)

    results = root.find("results")
    annotations = results.findall("annotation")

    target_url = f"{ROSSUM_CREDENTIALS.url}annotations/{annotation_id}"
    # Filter annotations based on the target URL
    matching_annotations = [
        annotation for annotation in annotations if annotation.get("url") == target_url
    ]
    # Check if exactly one annotation matches
    match len(matching_annotations):
        case 0:
            raise HTTPException(
                status_code=404,
                detail="Annotation id not found, available annotations: "
                + ", ".join(
                    [annotation.get("url").split("/")[-1] for annotation in annotations]
                ),
            )
        case 1:
            pass
        case _:
            raise HTTPException(
                status_code=400,
                detail1="Expected exactly one annotation to match the target ID, but found "
                + str(len(matching_annotations)),
            )

    # Create a new root for the filtered XML
    filtered_root = ET.Element("export")
    filtered_results = ET.SubElement(filtered_root, "results")

    # Add the single filtered annotation to the new results element
    filtered_results.append(matching_annotations[0])

    # Add pagination element as it was in the original XML
    pagination = root.find("pagination")
    filtered_root.append(pagination)

    # Convert the modified XML tree to a string
    filtered_xml_str = ET.tostring(filtered_root, encoding="utf-8").decode("utf-8")

    return filtered_xml_str
