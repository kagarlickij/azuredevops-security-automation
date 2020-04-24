import json
import argparse
import sys
import os
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--organization', type=str)
PARSER.add_argument('--feedId', type=str)
PARSER.add_argument('--projectName', type=str)
PARSER.add_argument('--groupName', type=str)
PARSER.add_argument('--groupSid', type=str)
PARSER.add_argument('--role', type=str)
PARSER.add_argument('--pat', type=str)

ARGS = PARSER.parse_args()

if not ARGS.feedId or not ARGS.groupName or not ARGS.groupSid or not ARGS.role or not ARGS.pat:
    print(f'##vso[task.logissue type=error] missing required arguments')
    sys.exit(1)

SID = (os.environ[(ARGS.groupSid).upper()])
DESCRIPTOR = f'Microsoft.TeamFoundation.Identity;{SID}'

if not ARGS.projectName:
    print(f'[INFO] no projectName received, so working with on-prem API')
    URL = '{}/_apis/packaging/Feeds/{}/permissions?api-version=5.0-preview.1'.format(ARGS.organization, ARGS.feedId)
else:
    print(f'[INFO] projectName received, so working with cloud API')
    URL = '{}/{}/_apis/packaging/Feeds/{}/permissions?api-version=5.0-preview.1'.format(ARGS.organization, ARGS.projectName, ARGS.feedId)

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
    CURRENT_ACL = RESPONSE.json()['value']

    for IDENTITY in CURRENT_ACL:
        if IDENTITY['identityDescriptor'] == DESCRIPTOR:
            CURRENT_ROLE = IDENTITY['role']
            break

    try:
        CURRENT_ROLE
    except NameError:
        print(f'##vso[task.logissue type=error] Group {ARGS.groupName} was not found')
        sys.exit(1)
    else:
        print(f'[INFO] Checking {ARGS.groupName} group permissions..')
        if CURRENT_ROLE == ARGS.role:
            print(f'[INFO] Current permissions match desired')
        else:
            print(f'##vso[task.logissue type=error] Current permissions do not match desired')
            print(f'##vso[task.logissue type=error] Desired permissions = {ARGS.role}')
            print(f'##vso[task.logissue type=error] Current permissions = {CURRENT_ROLE}')
            sys.exit(1)
