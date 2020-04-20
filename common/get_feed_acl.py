import json
import argparse
import sys
import os
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--organization', type=str, default='kagarlickij')
PARSER.add_argument('--feedId', type=str)
PARSER.add_argument('--projectName', type=str)
PARSER.add_argument('--groupName', type=str)
PARSER.add_argument('--groupAce', type=str)
PARSER.add_argument('--role', type=str)
PARSER.add_argument('--pat', type=str)

ARGS = PARSER.parse_args()

if not ARGS.feedId or not ARGS.groupName or not ARGS.groupAce or not ARGS.role or not ARGS.pat:
    print(f'[ERROR] missing required arguments')
    sys.exit(1)

ACE = (os.environ[(ARGS.groupAce).upper()])
FULL_ACE = f'Microsoft.TeamFoundation.Identity;{ACE}'

if not ARGS.projectName:
    print(f'[INFO] no projectName received, so working with on-prem API')
    URL = '{}/_apis/packaging/Feeds/{}/permissions?api-version=5.0-preview.1'.format(ARGS.organization, ARGS.feedId)
else:
    print(f'[INFO] projectName received, so working with cloud API')
    URL = 'https://feeds.dev.azure.com/{}/{}/_apis/packaging/Feeds/{}/permissions?api-version=5.0-preview.1'.format(ARGS.organization, ARGS.projectName, ARGS.feedId)

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
    CURRENT_ACL = RESPONSE.json()['value']

    for IDENTITY in CURRENT_ACL:
        if IDENTITY['identityDescriptor'] == FULL_ACE:
            CURRENT_ROLE = IDENTITY['role']
            break

    try:
        CURRENT_ROLE
    except NameError:
        print(f'[ERROR] Group {ARGS.groupName} was not found')
        sys.exit(1)
    else:
        print(f'[INFO] Checking {ARGS.groupName} group permissions..')
        if CURRENT_ROLE == ARGS.role:
            print(f'[INFO] Current permissions match desired')
        else:
            print(f'[ERROR] Current permissions do not match desired')
            print(f'[ERROR] Desired permissions = {ARGS.role}')
            print(f'[ERROR] Current permissions = {CURRENT_ROLE}')
            sys.exit(1)
