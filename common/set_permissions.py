import json
import argparse
import sys
import os
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--organization', type=str)
PARSER.add_argument('--namespaceId', type=str)
PARSER.add_argument('--projectId', type=str)
PARSER.add_argument('--groupName', type=str)
PARSER.add_argument('--groupSid', type=str)
PARSER.add_argument('--allow', type=str)
PARSER.add_argument('--deny', type=str)
PARSER.add_argument('--pat', type=str)

ARGS = PARSER.parse_args()

if not ARGS.projectId or not ARGS.groupName or not ARGS.groupSid or not ARGS.allow or not ARGS.deny or not ARGS.pat:
    print(f'##vso[task.logissue type=error] missing required arguments')
    sys.exit(1)

if ARGS.namespaceId == '2e9eb7ed-3c0a-47d4-87c1-0ffdd275fd87':
    print(f'[INFO] Git namespace, adding `repoV2` to token..')
    TOKEN = f'repoV2/{ARGS.projectId}'
elif ARGS.namespaceId == '52d39943-cb85-4d7f-8fa8-c6baac873819':
    print(f'[INFO] Project namespace, adding `$PROJECT:vstfs:///Classification/TeamProject` to token..')
    TOKEN = f'$PROJECT:vstfs:///Classification/TeamProject/{ARGS.projectId}'
elif ARGS.namespaceId == 'd34d3680-dfe5-4cc6-a949-7d9c68f73cba':
    print(f'[INFO] Analytics namespace, adding `$/Shared` to token..')
    TOKEN = f'$/Shared/{ARGS.projectId}'
elif ARGS.namespaceId == 'b7e84409-6553-448a-bbb2-af228e07cbeb':
    print(f'[INFO] Variable group namespace, adding `Library/` to token..')
    TOKEN = f'Library/{ARGS.projectId}'
else:
    print(f'[INFO] standart format for token')
    TOKEN = f'{ARGS.projectId}'

SID = (os.environ[(ARGS.groupSid).upper()])

URL = '{}/_apis/accesscontrollists/{}?token={}&api-version=5.0'.format(ARGS.organization, ARGS.namespaceId, TOKEN)
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
    CURRENT_ACL = RESPONSE.json()
    ACE = {
        'descriptor': f'Microsoft.TeamFoundation.Identity;{SID}',
        'allow': f'{ARGS.allow}',
        'deny': f'{ARGS.deny}'
    }

    if CURRENT_ACL['count'] == 0:
        ACCESS_DICT = {f'Microsoft.TeamFoundation.Identity;{SID}': ACE}
    else:
        ACCESS_DICT = CURRENT_ACL['value'][0]['acesDictionary']
        ACCESS_DICT[f'Microsoft.TeamFoundation.Identity;{SID}'] = ACE

    DESIRED_ACL = {'count': 1, 'value': [{'inheritPermissions': 'true', 'token': f'{TOKEN}', 'acesDictionary': ACCESS_DICT}]}

    URL = '{}/_apis/accesscontrollists/{}?api-version=5.0'.format(ARGS.organization, ARGS.namespaceId)
    HEADERS = {
        'Content-Type': 'application/json',
    }

    print(f'[INFO] Setting permissions for {ARGS.groupName} group..')
    try:
        RESPONSE = requests.post(URL, headers=HEADERS, data=json.dumps(DESIRED_ACL), auth=(ARGS.pat,''))
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
        RESPONSE_CODE = RESPONSE.status_code
        if RESPONSE_CODE == 204:
            print(f'[INFO] Permissions for {ARGS.groupName} group have been set successfully')
        else:
            print(f'##vso[task.logissue type=error] Permissions for {ARGS.groupName} group have not been set successfully')
            sys.exit(1)
