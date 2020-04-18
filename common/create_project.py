import json
import argparse
import sys
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--organization', type=str)
PARSER.add_argument('--projectName', type=str)
PARSER.add_argument('--projectDescription', type=str)
PARSER.add_argument('--processTemplate', type=str, default='6b724908-ef14-45cf-84f8-768b5384da45')
PARSER.add_argument('--pat', type=str)

ARGS = PARSER.parse_args()

if not ARGS.projectName or not ARGS.pat:
    print(f'[ERROR] missing required arguments')
    sys.exit(1)

print(f'[INFO] Creating {ARGS.projectName} project..')
URL = '{}/_apis/projects?api-version=5.0'.format(ARGS.organization)
HEADERS = {
    'Content-Type': 'application/json',
}

DATA = {
    'name': f'{ARGS.projectName}',
    'description': f'{ARGS.projectDescription}',
    'visibility': 'private',
    'capabilities': {
        'versioncontrol': {
            'sourceControlType': 'Git'
        },
        'processTemplate': {
            'templateTypeId': f'{ARGS.processTemplate}'
        }
    }
}

try:
    RESPONSE = requests.post(URL, headers=HEADERS, data=json.dumps(DATA), auth=(ARGS.pat,''))
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
    RESPONSE_CODE = RESPONSE.status_code
    if RESPONSE_CODE == 202:
        print(f'[INFO] Project {ARGS.projectName} has been created successfully')
    else:
        print(f'[ERROR] Project {ARGS.projectName} has not been created')
        sys.exit(1)