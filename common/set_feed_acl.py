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
    CURRENT_ACL = RESPONSE.json()
    ACCESS_DICT = CURRENT_ACL['value'][0]

    NEW_ACE = {
        'role': f'{ARGS.role}',
        'identityDescriptor': f'Microsoft.TeamFoundation.Identity;{ACE}',
        'displayName': 'None',
        'isInheritedRole': 'False'
    }

    DESIRED_ACL = [NEW_ACE]

    print(f'[INFO] Setting permissions for {ARGS.groupName} group..')
    try:
        RESPONSE = requests.patch(URL, headers=HEADERS, data=json.dumps(DESIRED_ACL), auth=(ARGS.pat,''))
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
        if RESPONSE_CODE == 200:
            print(f'[INFO] Permissions for {ARGS.groupName} group have been set successfully')
        else:
            print(f'[ERROR] Permissions for {ARGS.groupName} group have not been set successfully')
            sys.exit(1)
