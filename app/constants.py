import os
from dotenv import load_dotenv
from collections import namedtuple

AppCredentials = namedtuple("AppCredentials", ["username", "password"])
RossumCredentials = namedtuple("RossumCredentials", ["username", "password", "url"])

load_dotenv()


def load_app_credentials() -> AppCredentials:
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    if not username or not password:
        raise ValueError("Environment variables 'USERNAME' and 'PASSWORD' must be set.")
    return AppCredentials(username, password)


def load_rossum_credentials() -> RossumCredentials:
    rossum_username = os.getenv("ROSSUM_USERNAME")
    rossum_password = os.getenv("ROSSUM_PASSWORD")
    if not rossum_username or not rossum_password:
        raise ValueError(
            "Environment variables 'ROSSUM_USERNAME' and 'ROSSUM_PASSWORD' must be set."
        )

    # Assuming rossum url format follows this pattern
    special_characters = "!#$%&'*+/=?^`{|}~()<>[]:;.@,\"\\"
    rossum_base_url = rossum_username.translate(
        str.maketrans("", "", special_characters)
    )
    rossum_url = f"https://{rossum_base_url}.rossum.app/api/v1/"
    return RossumCredentials(rossum_username, rossum_password, rossum_url)


POSTBIN_URL = "https://www.postb.in/api/bin"

ROSSUM_CREDENTIALS = load_rossum_credentials()
APP_CREDENTIALS = load_app_credentials()
