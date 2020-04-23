import json
import argparse
import sys
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--organization', type=str)
PARSER.add_argument('--projectScopeDescriptor', type=str)
PARSER.add_argument('--groupName', type=str)
PARSER.add_argument('--desiredMembersQuantity', type=str)
PARSER.add_argument('--pat', type=str)

ARGS = PARSER.parse_args()

if not ARGS.projectScopeDescriptor or not ARGS.groupName or not ARGS.desiredMembersQuantity or not ARGS.pat:
    print(f'##vso[task.logissue type=error] missing required arguments')
    sys.exit(1)

URL = 'https://vssps.dev.azure.com/{}/_apis/graph/groups?scopeDescriptor={}&api-version=5.0-preview.1'.format(ARGS.organization, ARGS.projectScopeDescriptor)
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
            GROUP_ID = GROUP['originId']
            break

    try:
        GROUP_ID
    except NameError:
        print(f'##vso[task.logissue type=error] Group {ARGS.groupName} was not found')
        sys.exit(1)
    else:
        print(f'[INFO] Checking {ARGS.groupName} group..')
        URL = 'https://vsaex.dev.azure.com/{}/_apis/GroupEntitlements/{}/members?api-version=5.0-preview.1'.format(ARGS.organization, GROUP_ID)
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
            CURRENT_MEMBERS = RESPONSE.json()['members']
            CURRENT_MEMBERS_QUANTITY = len(CURRENT_MEMBERS)

            if CURRENT_MEMBERS_QUANTITY == int(ARGS.desiredMembersQuantity):
                print(f'[INFO] Current members quantity match desired')
            else:
                print(f'##vso[task.logissue type=error] Current members quantity does not match desired')
                print(f'##vso[task.logissue type=error] Desired members quantity = {ARGS.desiredMembersQuantity}')
                print(f'##vso[task.logissue type=error] Current members quantity = {CURRENT_MEMBERS_QUANTITY}')
                print(f'##vso[task.logissue type=error] Current members = {CURRENT_MEMBERS}')
                sys.exit(1)
