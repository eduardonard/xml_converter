# FastAPI Web App for Document Transformation and Posting

## Overview

This project is a FastAPI web application designed to interact with Rossum profiles. 

It provides an endpoint to log in, retrieve a document in XML format, transform the data, create a PostBin, convert the data to a base64 string, and post it on a PostBin, returning its URL. The application is protected by basic authentication and utilizes Docker for containerization and CI/CD pipelines for automated testing and deployment.

## Features

- **Endpoint**: `/export/queue_id/{queue_id}/annotation_id/{annotation_id}`
  - Logs into Rossum profile
  - Retrieves the document
  - Transforms xmls fields
  - Converts data to a base64 string
  - Creates a PostBin
  - Posts data to PostBin
  - Returns the bin url
- **Authentication**: Basic authentication to secure the endpoint
- **Testing**:
  - Unit tests with pytest
  - End-to-end tests with pytest
- **CI/CD Pipeline**:
  - Linting checks
  - Docker image build
  - Unit and end-to-end tests execution

## Requirements

- Docker
- Docker Compose

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/eduardonard/xml_converter.git
    cd yourproject
    ```

2. **Create an `.env` file**:
    Create a `.env` file in the root directory of the project with the following contents:
    ```env
    USERNAME=xml_converter_username
    PASSWORD=xml_converter_password
    ROSSUM_USERNAME=your_rossum_username
    ROSSUM_PASSWORD=your_rossum_password
    ```
    USERNAME and PASSWORD will be asked when a user will try to use an endpoint of the project.
    ROSSUM_USERNAME and ROSSUM_PASSWORD are the ones used to login to Rossum.
    Basic Auth sends credentials as Base64-encoded strings, which are not encrypted, making them susceptible to interception without SSL/TLS. Rossum supports https connections, so there are no vulnerability issues.

3. **Build and run the Docker container**:
    ```bash
    docker-compose up --build
    ```

## Usage

To use the endpoint, make a GET request to the following URL with the appropriate `queue_id` and `annotation_id`, and include your basic authentication credentials:
```
http://localhost:8000/export/queue_id/{queue_id}/annotation_id/{annotation_id}
```
Replace `{queue_id}` and `{annotation_id}` with the actual values.

## Testing

The project includes unit and end-to-end tests using pytest. The CI/CD pipeline and docker-compose up automatically run these tests, but you can also run them separately locally:

0. **Install pytest**
    ```bash
    pip install pytest
    ```

1. **Unit Tests**:
    ```bash
    pytest tests -m unit
    ```

2. **End-to-End Tests**:
    ```bash
    pytest tests -m integration
    ```

Integration tests use a specific Rossum user, if you change the user make sure to change the path parameters.

## CI/CD Pipeline

The project uses GitHub Actions for CI/CD. The pipeline performs the following tasks:
- Checks code linting
- Builds the Docker image
- Runs unit and end-to-end tests

Secrets for the pipeline (e.g., Rossum credentials) are stored in GitHub Secrets.