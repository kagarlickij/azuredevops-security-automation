import json
import argparse
import sys
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--organization', type=str)
PARSER.add_argument('--projectScopeDescriptor', type=str)
PARSER.add_argument('--desiredGroupsList', nargs='+')
PARSER.add_argument('--pat', type=str)

ARGS = PARSER.parse_args()

if not ARGS.projectScopeDescriptor or not ARGS.desiredGroupsList or not ARGS.pat:
    print(f'[ERROR] missing required arguments')
    sys.exit(1)

DESIRED_GROUPS_LIST = ARGS.desiredGroupsList

URL = '{}/_apis/graph/groups?scopeDescriptor={}&api-version=5.0-preview.1'.format(ARGS.organization, ARGS.projectScopeDescriptor)
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
    CURRENT_GROUPS_LIST = []
    GROUPS = RESPONSE.json()['value']

    for GROUP in GROUPS:
        groupDisplayName = GROUP['displayName']
        CURRENT_GROUPS_LIST.append(groupDisplayName)

    DESIRED_GROUPS_LIST.sort()
    CURRENT_GROUPS_LIST.sort()
    if CURRENT_GROUPS_LIST == DESIRED_GROUPS_LIST:
        print(f'[INFO] Current list of groups match desired')
    else:
        print(f'[ERROR] Current list of groups does not match desired')
        print(f'[ERROR] currentGroupsList = {CURRENT_GROUPS_LIST}')
        print(f'[ERROR] desiredGroupsList = {DESIRED_GROUPS_LIST}')
        sys.exit(1)
