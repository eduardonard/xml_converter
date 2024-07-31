import pytest
import xml.etree.ElementTree as ET
from app.transform_xml import transform_invoice_xml


def read_xml_to_string(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    xml_string = ET.tostring(root, encoding="unicode")
    return xml_string


input_xml = read_xml_to_string("data/xmls/input.xml")
expected_xml = read_xml_to_string("data/xmls/output.xml")
wrong_output_xml = read_xml_to_string("data/xmls/output_wrong.xml")


@pytest.mark.unit
def test_transform_invoice_xml():
    result = transform_invoice_xml(input_xml)

    assert result == expected_xml


@pytest.mark.unit
def test_transform_wrong_invoice_xml():
    result = transform_invoice_xml(input_xml)

    assert result != wrong_output_xml
