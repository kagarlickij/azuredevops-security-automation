import json
import argparse
import sys
import base64
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--organization', type=str)
PARSER.add_argument('--projectScopeDescriptor', type=str)
PARSER.add_argument('--groupName', type=str)
PARSER.add_argument('--groupAce', type=str)
PARSER.add_argument('--pat', type=str)

ARGS = PARSER.parse_args()

if not ARGS.projectScopeDescriptor or not ARGS.groupName or not ARGS.groupAce or not ARGS.pat:
    print(f'##vso[task.logissue type=error] missing required arguments')
    sys.exit(1)

URL = '{}/_apis/graph/groups?scopeDescriptor={}&api-version=5.0-preview.1'.format(ARGS.organization, ARGS.projectScopeDescriptor)
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
    GROUPS = RESPONSE.json()['value']

    for GROUP in GROUPS:
        if GROUP['displayName'] == ARGS.groupName:
            GROUP_DESCRIPTOR = GROUP['descriptor']
            break

    try:
        GROUP_DESCRIPTOR
    except NameError:
        print(f'##vso[task.logissue type=error] Group {ARGS.groupName} was not found')
        sys.exit(1)
    else:
        print(f'[INFO] Checking {ARGS.groupName} group..')
        DESCRIPTOR = GROUP_DESCRIPTOR.split('vssgp.',1)[1]

        for SYM in DESCRIPTOR.split('.'):
            ACE = base64.b64decode(SYM + '=' * (-len(SYM) % 4)).decode('utf-8')
            print(f'[INFO] Group {ARGS.groupName} ACE = {ACE}')
            print(f'##vso[task.setvariable variable={ARGS.groupAce}]{ACE}')
