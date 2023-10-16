import pandas as pd
import json
import datetime
import re
from icecream import ic
import os 
from simple_salesforce import Salesforce, SalesforceLogin, SFType
import re

def get_json_value(json_file, key, sub_key):
   try:
       with open(json_file) as f:
           data = json.load(f)
           return data[key][sub_key]
   except Exception as e:
       ic("Error: ", e)

def get_secret(secret_name):
    try:
       return get_json_value('secrets.json', 'secrets', secret_name)
    except Exception as e:
        ic("Error: ", e)
        


def clean_c(text):
    if text is None:
        return ''
    else:
        # Remove CDATA tags
        pattern = re.compile(r'<!\[CDATA\[|\]\]>')
        text = pattern.sub('', text)
        # Remove Unicode tags
        pattern = re.compile(r'\\u\w{4}')
        text = pattern.sub('', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        # Remove \t character
        text = text.replace('\\t', '')
        # Remove any remaining backslashes
        text = text.replace('\\', '')
        return text 

def truncate_string(text):
    if len(text) > 245:
        return text[:245]
    else:
        return text

def convert_date(date_str):
    try:
        offset = None
        timestamp = int(date_str[6:-7])
        offset_str = re.search(r'[-+]\d{4}', date_str).group()
        offset = int(offset_str[:3]) * 60 + int(offset_str[3:])
        dt = datetime.datetime.utcfromtimestamp(timestamp / 1000)
        dt = dt.replace(tzinfo=datetime.timezone(datetime.timedelta(minutes=offset)))
        return dt.isoformat()
    except (ValueError, IndexError):
        if offset is None:
            raise ValueError("Invalid date string: {date_str}")
        return None

sfUser=get_secret('sfUser')
sfPass=get_secret('sfPass')
sfToken=get_secret('sfToken')


sf = Salesforce(username=sfUser, password=sfPass, security_token=sfToken)
app = SFType('Application__c', sf.session_id, sf.sf_instance)

ic(sf.session_id, sf.sf_instance, sf.version)

def upsert_row(row):
    try:
        applicant_name = clean_c(row.FirstName) + ' ' + clean_c(row.LastName)
        upsert_data = {
            'NGAppSource__c': row.Application_Source,
            'App_Recieved__c': row.DateReceived_ISO,
            'NG_DateRecieved__c': row.DateReceived_ISO, 
            'NGCity__c': clean_c(row.CityName),
            'NG__c': clean_c(row.Country),
            'NG_Additional_Info__c': truncate_string(clean_c(row.AdditionalInfo)),
            'NG_Custom_Questions__c': clean_c(row.CustomQuestions),
            'NG_Educational_Experience__c': clean_c(row.EducationalExperienceList),
            'NG_Work_Experiences__c': clean_c(row.WorkExperienceList),
            'NG_Salary__c': clean_c(row.SalaryAmount),
            'NG_Salary_Period__c': clean_c(row.SalaryPeriod),
            'NG_JobTitle__c': clean_c(row.JobTitle),
            'Email_Address__c': clean_c(row.EmailAddress),
            'Applicant_Name__c': applicant_name,
            'NG_Resume_Link__c': clean_c(row.ResumeURL),
            'State__c': clean_c(row.StateName),
            'Street_Address__c': clean_c(row.StreetAddress),
            'NG_Personal_References__c': clean_c(row.PersonalReferenceList),
            'Phone_Number__c': clean_c(row.PhoneNumber)
            }
        ic(upsert_data)
        app.upsert('NGAppID__c/' + row.ApplicationID, upsert_data)
        ic()
    except Exception as e:
        ic(e)
        ic(row)
        ic(upsert_data)
        

last_timestamp = None

if os.path.exists('last.json'):
    with open('last.json', 'rb') as f:
        data = json.load(f)
        last_df = pd.json_normalize(data)
        last_timestamp = last_df['DateReceived'].max()

if os.path.exists('data.json'):
    df = pd.read_json('data.json')
else:
    exception = Exception("No json file found")


if last_timestamp is not None:
    df = df[df['DateReceived'] > last_timestamp]
    ic()
df['DateReceived_ISO'] = df['DateReceived'].apply(convert_date)
df.fillna("none", inplace=True)
df['CustomQuestions'] = df['CustomQuestions'].apply(json.dumps)
df['EducationalExperienceList'] = df['EducationalExperienceList'].apply(json.dumps)
df['WorkExperienceList'] = df['WorkExperienceList'].apply(json.dumps)   
df['PersonalReferenceList'] = df['PersonalReferenceList'].apply(json.dumps)   

for row in df.itertuples(index=False):
    upsert_row(row)
    ic(row.ApplicationID, row.DateReceived_ISO)

ic()