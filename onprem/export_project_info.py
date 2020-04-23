import json
import argparse
import sys
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--organization', type=str)
PARSER.add_argument('--projectName', type=str)
PARSER.add_argument('--pat', type=str)

ARGS = PARSER.parse_args()

if not ARGS.projectName or not ARGS.pat:
    print(f'##vso[task.logissue type=error] missing required arguments')
    sys.exit(1)

URL = '{}/_apis/projects?api-version=5.0'.format(ARGS.organization)
HEADERS = {
    'Content-Type': 'application/json',
}

try:
    RESPONSE = requests.get(URL, headers=HEADERS, auth=(ARGS.pat,''))
    RESPONSE.raise_for_status()
except Exception as err:
    print(f'##vso[task.logissue type=error] {err}')
    RESPONSE_TEXT = json.loads(RESPONSE.text)
    CODE = RESPONSE_TEXT['errorCode']
    MESSAGE = RESPONSE_TEXT['message']
    print(f'##vso[task.logissue type=error] Response code: {CODE}')
    print(f'##vso[task.logissue type=error] Response message: {MESSAGE}')
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
