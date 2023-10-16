# ng-sf

ng-sf is a simple python script which imports job applications from NinjaGig and exports them to custom object in Salesforce

## Secrets File

ng-sf requires a secrets file to be created in the same directory as the script. The file should be named secrets.json and use the following format:

    {
        "secrets": {
            "ngJson": "INSERT NINJAGIG JSON URL HERE",
            "sfUser": "INSERT USERNAME HERE",
            "sfPass": "INSERT PASSWORD HERE",
            "sfToken": "INSERT TOKEN HERE"
        }
    }

## Custom Object in Salesforce

    Your salesforce instance will need to have a custom object 'Application__c' created.

    This object will need the following custom fields:
    Applicant_Name__c #Text
    App_Recieved__c #Date
    App_Status__c #Picklist
    Education__c #Text
    Email_Address__c #Email
    NGAppID__c #Text (External ID)
    NGAppSource__c #Text
    NGCity__c #Text
    NG_Additional_Info__c #Long Text Area
    NG_Custom_Questions__c #Long Text Area
    NG_DateRecieved__c #Date
    NG_Educational_Experience__c #Long Text Area
    NG_JobTitle__c #Text
    NG_Personal_References__c #Long Text Area
    NG_Resume_Link__c #URL
    NG_Salary_Period__c #Text
    NG_Salary__c #Number
    NG_Work_Experiences__c #Long Text Area
    NG__c #Text
    Phone_Number__c #Phone
    State__c #Text
    Street_Address__c #Text
    Years_Experience__c #Number

## Customize Script

This script was written for a specific use case and you should feel free to customize it to meet your needs.

## Contributing

Pull requests are welcome.

## License

[MIT](https://choosealicense.com/licenses/mit/)
