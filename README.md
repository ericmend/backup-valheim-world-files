
### backup-valheim-world-files

Script for backup on google drive, files related to the world of valheim

## Credentials :
[Google service-account](https://cloud.google.com/docs/authentication/getting-started)

[Enabling Google Drive API](https://console.cloud.google.com/apis/dashboard)

## Setup and activate virtual environment :
For Unix based systems please execute the following command to create venv and install requirements.
```
make init
source .venv/bin/activate
```

#### Manual installation :
```
python3 -m pip install virtualenv
python3 -m venv .env
./env/bin/python3 -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

#### Global script :

`python app/main.py --world WORLD --path PATH --drive_folder DRIVE_FOLDER --service_account_file SERVICE_ACCOUNT_FILE`

or

`./run-backup.sh`