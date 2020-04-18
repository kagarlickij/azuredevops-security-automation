import json
import argparse
import sys
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--organization', type=str, default='kagarlickij')
PARSER.add_argument('--projectName', type=str)
PARSER.add_argument('--pat', type=str)

ARGS = PARSER.parse_args()

if not ARGS.projectName or not ARGS.pat:
    print(f'[ERROR] missing required arguments')
    sys.exit(1)

URL = 'https://dev.azure.com/{}/_apis/projects?api-version=5.0'.format(ARGS.organization)
HEADERS = {
    'Content-Type': 'application/json',
}

try:
    RESPONSE = requests.get(URL, headers=HEADERS, auth=(ARGS.pat,''))
    RESPONSE.raise_for_status()
except Exception as err:
    print(f'[ERROR] {err}')
    RESPONSE_TEXT = json.loads(RESPONSE.text)
    CODE = RESPONSE_TEXT['errorCode']
    MESSAGE = RESPONSE_TEXT['message']
    print(f'[ERROR] Response code: {CODE}')
    print(f'[ERROR] Response message: {MESSAGE}')
    sys.exit(1)
else:
    PROJECT_LIST = RESPONSE.json()['value']

    for PROJECT in PROJECT_LIST:
        if PROJECT['name'] == ARGS.projectName:
            PROJECT_ID = PROJECT['id']
            break

    try:
        PROJECT_ID
    except NameError:
        print('[ERROR] projectId has not been obtained')
        sys.exit(1)
    else:
        print(f'[INFO] projectId = {PROJECT_ID}')
        print(f'##vso[task.setvariable variable=projectId]{PROJECT_ID}')

print('Getting projectScopeDescriptor..')
URL = 'https://vssps.dev.azure.com/{}/_apis/graph/descriptors/{}?api-version=5.0-preview.1'.format(ARGS.organization, PROJECT_ID)
HEADERS = {
    'Content-Type': 'application/json',
}

try:
    RESPONSE = requests.get(URL, headers=HEADERS, auth=(ARGS.pat,''))
    RESPONSE.raise_for_status()
except Exception as err:
    print(f'[ERROR] {err}')
    RESPONSE_TEXT = json.loads(RESPONSE.text)
    CODE = RESPONSE_TEXT['errorCode']
    MESSAGE = RESPONSE_TEXT['message']
    print(f'[ERROR] Response code: {CODE}')
    print(f'[ERROR] Response message: {MESSAGE}')
    sys.exit(1)
else:
    PROJECT_SCOPE_DESCRIPTOR = RESPONSE.json()['value']

    try:
        PROJECT_SCOPE_DESCRIPTOR
    except NameError:
        print('[ERROR] projectScopeDescriptor has not been obtained')
        sys.exit(1)
    else:
        print(f'[INFO] projectScopeDescriptor = {PROJECT_SCOPE_DESCRIPTOR}')
        print(f'##vso[task.setvariable variable=projectScopeDescriptor]{PROJECT_SCOPE_DESCRIPTOR}')
