"""Import modules."""
import json
import os
import requests
from icecream import ic


def get_json_value(json_file, key, sub_key):
    """
    Get the value of a sub_key in a JSON file.

    Args:
        json_file (str): The path to the JSON file.
        key (str): The key in the JSON file.
        sub_key (str): The sub_key in the JSON file.

    Returns:
        The value of the sub_key in the JSON file.

    Raises:
        FileNotFoundError: If the JSON file is not found.
        KeyError: If the key or sub_key is not found in the JSON file.
    """
    try:
        with open(json_file, encoding="utf-8") as myfile:
            f_data = json.load(myfile)
            return f_data[key][sub_key]
    except FileNotFoundError as file_err:
        ic("Error: ", file_err)
        raise
    except KeyError as key_err:
        ic("Error: ", key_err)
        raise


def get_secret(secret_name):
    """
    Get the value of a secret from the secrets.json file.

    Args:
        secret_name (str): The name of the secret to retrieve.

    Returns:
        The value of the secret.

    Raises:
        FileNotFoundError: If the secrets.json file is not found.
        KeyError: If the secret_name is not found in the secrets.json file.
    """
    try:
        return get_json_value("secrets.json", "secrets", secret_name)
    except (FileNotFoundError, KeyError) as sec_err:
        ic("Error: ", sec_err)
        raise


ngJson = get_secret("ngJson")

# Remove the data.new file if it exists
if os.path.exists("data.new"):
    os.remove("data.new")
    ic("Removed data.new")

# Download the JSON data from the URL, abort if anything goes wrong.
# Sometimes Ninjagig is slow to respond, so we set a timeout of 15 seconds.
try:
    response = requests.get(ngJson, timeout=15)
except requests.exceptions.RequestException as err:
    ic("Error: ", err)
    raise SystemExit(err) from err
data = response.json()
ic("Downloaded JSON data")

# Set the downloaded JSON data as data.new
with open("data.new", "w", encoding="utf-8") as file:
    json.dump(data, file)
    ic("Wrote JSON data to data.new")

# Check if data.new is larger than data.json
if os.path.exists("data.json") and os.path.getsize("data.new") > os.path.getsize(
    "data.json"
):
    ic("Data validity check passed")
    # Remove last.json if it exists
    if os.path.exists("last.json"):
        os.remove("last.json")
        ic("Removed last.json")
    # Rename data.json to last.json
    os.rename("data.json", "last.json")
    ic("Renamed data.json to last.json")
    # Rename data.new to data.json
    os.rename("data.new", "data.json")
    ic("Renamed data.new to data.json")
else:
    # Remove data.new if it exists
    ic("No new data since last process or data failed validity check")
    if os.path.exists("data.new"):
        ic("Removing data.new")
        os.remove("data.new")
