# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import os.path
import subprocess
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

FILENAME:str = None
MIMETYPE:str = 'application/gzip'

# The body contains the metadata for the file.
def __body(args):
    return {
        'name': FILENAME,
        'title': 'World {}'.format(args.world),
        'description': '{} world backup.'.format(args.world),
        'parents': [ args.drive_folder ]
        }

# Insert a file. Files are comprised of contents and metadata.
# MediaFileUpload abstracts uploading file contents from a file on disk.
def __mediaBody(args):
    return MediaFileUpload(
        os.path.join(args.path, FILENAME),
        mimetype=MIMETYPE,
        resumable=True
    )

def __bash(command):
    try:
        print(command)
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"\n\nNão foi possível executar o comando em bash\nMotivo do erro: {e.output}")
    
def __find(service, args):
    print('Consultando item...')
    start = time.time()
    message = ''
    try:
        results = service.files().list(q="'" + args.drive_folder + "' in parents",
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

def __create(service, args):
    print('Criando item...')
    start = time.time()
    message = ''
    try:
        new_file = service.files().create(
                    body=__body(args),
                    media_body=__mediaBody(args),
                    fields='id,name').execute()
        file_name = new_file.get('name')
        if file_name != FILENAME:
            message = 'não '    
        message = f"Arquivo {FILENAME} {message}foi criado!!"
    except Exception as e:
        raise RuntimeError(f"\n\nNão foi possível criar o arquivo {FILENAME}\nMotivo do erro: {e}")
    finally:
        print(f'{message}; tempo: {time.time() - start}')
        
def __update(service, args, itemId):
    print('Atualizando item...')
    start = time.time()
    message = ''
    try:
        body = __body(args)
        body['parents'] = None
        updated_file = service.files().update(
            fileId=itemId,
            body=body,
            media_body=__mediaBody(args),
            fields='id,name').execute()
        file_name = updated_file.get('name')
        if file_name != FILENAME:
            message = 'não '    
        message = f"Arquivo {FILENAME} {message}foi atualizado!!"
    except Exception as e:
        raise RuntimeError(f"\n\nNão foi possível atualizar o arquivo {FILENAME}\nMotivo do erro: {e}")
    finally:
        print(f'{message}; tempo: {time.time() - start}')
        
def __main(args):
    
    COMMAND_TAR_GZ:str = 'cd {} && tar -zcvf {} {}.db {}.fwl'.format(args.path, FILENAME, args.world, args.world)
    __bash(COMMAND_TAR_GZ)

    credentials = service_account.Credentials.from_service_account_file(args.service_account_file)
    service = build('drive', 'v3', credentials=credentials)

    try:
        item = __find(service, args)
        
        if not item:
            __create(service, args)
        else:
            __update(service, args, item['id'])

    except HttpError as error:
        print(f'Ocorreu um erro: {error}')

if __name__ == '__main__':
    args = argparse.ArgumentParser(description="Backup Valheim World Files")
    args.add_argument('--world', help="File name for backup", required=True)
    args.add_argument('--path', help="Location of the file to be copied", required=True)
    args.add_argument('--drive_folder', help="Drive folder ID in Google Drive", required=True)
    args.add_argument('--service_account_file', help="Google Drive service account json file", required=True)
    args = args.parse_args()
    FILENAME = '{}.tar.gz'.format(args.world)
    __main(args)

