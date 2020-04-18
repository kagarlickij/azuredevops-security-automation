import json
import argparse
import sys
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--organization', type=str, default='kagarlickij')
PARSER.add_argument('--projectScopeDescriptor', type=str)
PARSER.add_argument('--groupName', type=str)
PARSER.add_argument('--pat', type=str)

ARGS = PARSER.parse_args()

if not ARGS.projectScopeDescriptor or not ARGS.groupName or not ARGS.pat:
    print(f'[ERROR] missing required arguments')
    sys.exit(1)

URL = 'https://vssps.dev.azure.com/{}/_apis/graph/groups?scopeDescriptor={}&api-version=5.0-preview.1'.format(ARGS.organization, ARGS.projectScopeDescriptor)
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
    GROUPS = RESPONSE.json()['value']

    for GROUP in GROUPS:
        if GROUP['displayName'] == ARGS.groupName:
            GROUP_DESCRIPTOR = GROUP['descriptor']
            break

    try:
        GROUP_DESCRIPTOR
    except NameError:
        print(f'[ERROR] Group {ARGS.groupName} was not found')
        sys.exit(1)
    else:
        print(f'[INFO] Deleting {ARGS.groupName} group..')
        URL = 'https://vssps.dev.azure.com/{}/_apis/graph/groups/{}?api-version=5.0-preview.1'.format(ARGS.organization, GROUP_DESCRIPTOR)
        HEADERS = {
            'Content-Type': 'application/json',
        }

        try:
            RESPONSE = requests.delete(URL, headers=HEADERS, auth=(ARGS.pat,''))
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
            if RESPONSE_CODE == 204:
                print(f'[INFO] {ARGS.groupName} group has been deleted successfully')
            else:
                print(f'[ERROR] {ARGS.groupName} group has not been deleted successfully')
                sys.exit(1)
