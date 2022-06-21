# -*- coding: utf-8 -*-
from __future__ import print_function

import os.path
import subprocess
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

# python3 -m pip install virtualenv
# python3 -m venv env
# ./env/bin/python3 -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
# ./env/bin/python3 -m pip install -U nuitka
# ./env/bin/python3 -m pip freeze > requirements.txt
# ./env/bin/python3 -m pip install -r requirements.txt
# ./env/bin/python3 -m nuitka --follow-imports --standalone app/main.py
# ./env/bin/python3 -m nuitka --follow-imports app/main.py -o bin/backup-valheim-world-files
# ./env/bin/python3 -B app/main.py

# define os parametros
WORLD:str = 'flere'
PATH:str = '/home/ubuntu/.config/unity3d/IronGate/Valheim/worlds'
DRIVE_FOLDER:str = '1LPcMMx6r-8IKx4quBj5UKipC2c4pkFAV'
SERVICE_ACCOUNT_FILE:str = 'credentials.json'

FILENAME:str = '{}.tar.gz'.format(WORLD)
MIMETYPE:str = 'application/gzip'
TITLE:str = 'World {}'.format(WORLD)
DESCRIPTION:str = '{} world backup.'.format(WORLD)
COMMAND_TAR_GZ:str = 'cd {} && tar -zcvf {}.tar.gz {}.db {}.fwl'.format(PATH, WORLD, WORLD, WORLD)

# The body contains the metadata for the file.
def __body():
    return {
        'name': FILENAME,
        'title': TITLE,
        'description': DESCRIPTION,
        'parents': [ DRIVE_FOLDER ]
        }

# Insert a file. Files are comprised of contents and metadata.
# MediaFileUpload abstracts uploading file contents from a file on disk.
def __mediaBody():
    return MediaFileUpload(
        os.path.join(PATH, FILENAME),
        mimetype=MIMETYPE,
        resumable=True
    )

def __bash(command):
    try:
        print(command)
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"\n\nNão foi possível executar o comando em bash\nMotivo do erro: {e.output}")
    
def __find(service):
    print('Consultando item...')
    start = time.time()
    message = ''
    try:
        results = service.files().list(q="'" + DRIVE_FOLDER + "' in parents",
                                       pageSize=10,
                                       fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        item = next((item for item in items if item['name'] == FILENAME), None)
        if not item:
            message = 'Não foi '
        message = f'{message}Encontrado item!!'
        
        return item
    except Exception as e:
        raise RuntimeError(f"\n\nNão foi possível encontrar o arquivo {FILENAME}\nMotivo do erro: {e}")
    finally:
        print(f'{message}; tempo: {time.time() - start}')

def __create(service):
    print('Criando item...')
    start = time.time()
    message = ''
    try:
        new_file = service.files().create(
                    body=__body,
                    media_body=__mediaBody(),
                    fields='id,name').execute()
        file_name = new_file.get('name')
        if file_name != FILENAME:
            message = 'não '    
        message = f"Arquivo {FILENAME} {message}foi criado!!"
    except Exception as e:
        raise RuntimeError(f"\n\nNão foi possível criar o arquivo {FILENAME}\nMotivo do erro: {e}")
    finally:
        print(f'{message}; tempo: {time.time() - start}')
        
def __update(service, itemId):
    print('Atualizando item...')
    start = time.time()
    message = ''
    try:
        body = __body()
        body['parents'] = None
        updated_file = service.files().update(
            fileId=itemId,
            body=body,
            media_body=__mediaBody(),
            fields='id,name').execute()
        file_name = updated_file.get('name')
        if file_name != FILENAME:
            message = 'não '    
        message = f"Arquivo {FILENAME} {message}foi atualizado!!"
    except Exception as e:
        raise RuntimeError(f"\n\nNão foi possível atualizar o arquivo {FILENAME}\nMotivo do erro: {e}")
    finally:
        print(f'{message}; tempo: {time.time() - start}')
        
def __main():
    
    __bash(COMMAND_TAR_GZ)
        
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
    
    service = build('drive', 'v3', credentials=credentials)

    try:
        item = __find(service)
        
        if not item:
            __create(service)
        else:
            __update(service, item['id'])

    except HttpError as error:
        print(f'Ocorreu um erro: {error}')

if __name__ == '__main__':
    __main()