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

## Contributing

Pull requests are welcome. 

## License

[MIT](https://choosealicense.com/licenses/mit/)