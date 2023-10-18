"""Import  datatime module    """
import datetime
import json
import os
import re

import pandas as pd
from icecream import ic
from simple_salesforce import Salesforce, SFType
from simple_salesforce.exceptions import SalesforceError

# initialize variables
last_timestamp = None


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
        with open(json_file, encoding="utf-8") as file:
            f_data = json.load(file)
            return f_data[key][sub_key]
    except FileNotFoundError as err:
        ic("Error: ", err)
        raise
    except KeyError as err:
        ic("Error: ", err)
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
    except (FileNotFoundError, KeyError) as err:
        ic("Error: ", err)
        raise


def clean_c(text):
    """
    Clean a string by removing CDATA tags, Unicode tags, leading/trailing
    whitespace, \t characters, and backslashes.

    Args:
        text (str): The string to clean.

    Returns:
        The cleaned string.
    """
    if text is None:
        return ""
    else:
        # Remove CDATA tags
        pattern = re.compile(r"<!\[CDATA\[|\]\]>")
        text = pattern.sub("", text)
        # Remove Unicode tags
        pattern = re.compile(r"\\u\w{4}")
        text = pattern.sub("", text)
        # Remove leading/trailing whitespace
        text = text.strip()
        # Remove \t character
        text = text.replace("\\t", "")
        # Remove any remaining backslashes
        text = text.replace("\\", "")
        return text


def truncate_string(text):
    """
    Truncate a string to 245 characters.

    Args:
        text (str): The string to truncate.

    Returns:
        The truncated string.
    """
    if len(text) > 245:
        return text[:245]
    else:
        return text


def convert_date(date_str):
    """
    Convert a date string to an ISO-formatted datetime string.

    Args:
        date_str (str): The date string to convert.

    Returns:
        The ISO-formatted datetime string.

    Raises:
        ValueError: If the date string is invalid.
    """
    try:
        offset = None
        timestamp = int(date_str[6:-7])
        offset_str = re.search(r"[-+]\d{4}", date_str).group()
        offset = int(offset_str[:3]) * 60 + int(offset_str[3:])
        dt = datetime.datetime.utcfromtimestamp(timestamp / 1000)
        dt = dt.replace(tzinfo=datetime.timezone(datetime.timedelta(minutes=offset)))
        return dt.isoformat()
    except (ValueError, IndexError) as exc:
        if offset is None:
            raise ValueError(f"Invalid date string: {date_str}") from exc
        else:
            raise ValueError(f"Invalid date string: {date_str}") from exc


sfUser = get_secret("sfUser")
sfPass = get_secret("sfPass")
sfToken = get_secret("sfToken")


sf = Salesforce(username=sfUser, password=sfPass, security_token=sfToken)
app = SFType("Application__c", sf.session_id, sf.sf_instance)

ic(sf.session_id, sf.sf_instance, sf.version)


def upsert_row(row_data):
    """
    Upserts a row of data to Salesforce.

    Args:
        row_data (pandas.core.series.Series): The row of data to upsert.

    Raises:
        Exception: If there is an error upserting the row.
    """
    try:
        applicant_name = clean_c(row_data.FirstName) + " " + clean_c(row_data.LastName)
        upsert_data = {
            "NGAppSource__c": row_data.Application_Source,
            "App_Recieved__c": row_data.DateReceived_ISO,
            "NG_DateRecieved__c": row_data.DateReceived_ISO,
            "NGCity__c": clean_c(row_data.CityName),
            "NG__c": clean_c(row_data.Country),
            "NG_Additional_Info__c": truncate_string(clean_c(row_data.AdditionalInfo)),
            "NG_Custom_Questions__c": clean_c(row_data.CustomQuestions),
            "NG_Educational_Experience__c": clean_c(row_data.EducationalExperienceList),
            "NG_Work_Experiences__c": clean_c(row_data.WorkExperienceList),
            "NG_Salary__c": clean_c(row_data.SalaryAmount),
            "NG_Salary_Period__c": clean_c(row_data.SalaryPeriod),
            "NG_JobTitle__c": clean_c(row_data.JobTitle),
            "Email_Address__c": clean_c(row_data.EmailAddress),
            "Applicant_Name__c": applicant_name,
            "NG_Resume_Link__c": clean_c(row_data.ResumeURL),
            "State__c": clean_c(row_data.StateName),
            "Street_Address__c": clean_c(row_data.StreetAddress),
            "NG_Personal_References__c": clean_c(row_data.PersonalReferenceList),
            "Phone_Number__c": clean_c(row_data.PhoneNumber),
        }
        ic(upsert_data)
        app.upsert("NGAppID__c/" + row_data.ApplicationID, upsert_data)
        ic()
    except SalesforceError as err:
        ic(err)


if os.path.exists("last.json"):
    with open("last.json", "rb") as f:
        data = json.load(f)
        last_df = pd.json_normalize(data)
        last_timestamp = last_df["DateReceived"].max()
else:
    ic("No last.json file found")
    last_timestamp = None


if os.path.exists("data.json"):
    df = pd.read_json("data.json")
else:
    raise FileNotFoundError("No json file found")

if last_timestamp is not None:
    df = df[df["DateReceived"] > last_timestamp]
    ic()


df["DateReceived_ISO"] = df["DateReceived"].apply(convert_date)
df.fillna("none", inplace=True)
df["CustomQuestions"] = df["CustomQuestions"].apply(json.dumps)
df["EducationalExperienceList"] = df["EducationalExperienceList"].apply(json.dumps)
df["WorkExperienceList"] = df["WorkExperienceList"].apply(json.dumps)
df["PersonalReferenceList"] = df["PersonalReferenceList"].apply(json.dumps)

for row in df.itertuples(index=False):
    try:
        upsert_row(row)
        ic(row.ApplicationID, row.DateReceived_ISO)
    except SalesforceError as e:
        ic(e)
ic()
