"""
This script gets current ACL and compares it with desired
"""

import json
import argparse
import sys
import os
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--organization', type=str, required=True)
PARSER.add_argument('--namespaceId', type=str, required=True)
PARSER.add_argument('--projectId', type=str, required=True)
PARSER.add_argument('--groupName', type=str, required=True)
PARSER.add_argument('--groupSid', type=str, required=True)
PARSER.add_argument('--allow', type=str, required=True)
PARSER.add_argument('--deny', type=str, required=True)
PARSER.add_argument('--pat', type=str, required=True)

ARGS = PARSER.parse_args()

if ARGS.namespaceId == '2e9eb7ed-3c0a-47d4-87c1-0ffdd275fd87':
    print('[INFO] Git namespace, adding `repoV2` to token..')
    TOKEN = f'repoV2/{ARGS.projectId}'
elif ARGS.namespaceId == '52d39943-cb85-4d7f-8fa8-c6baac873819':
    print('[INFO] Project namespace, adding `$PROJECT:vstfs:///Classification/TeamProject` to token..')
    TOKEN = f'$PROJECT:vstfs:///Classification/TeamProject/{ARGS.projectId}'
elif ARGS.namespaceId == 'd34d3680-dfe5-4cc6-a949-7d9c68f73cba':
    print('[INFO] Analytics namespace, adding `$/Shared` to token..')
    TOKEN = f'$/Shared/{ARGS.projectId}'
elif ARGS.namespaceId == 'b7e84409-6553-448a-bbb2-af228e07cbeb':
    print('[INFO] Variable group namespace, adding `Library/` to token..')
    TOKEN = f'Library/{ARGS.projectId}'
else:
    print('[INFO] standart format for token')
    TOKEN = f'{ARGS.projectId}'

SID = (os.environ[(ARGS.groupSid).upper()])
DESCRIPTOR = f'Microsoft.TeamFoundation.Identity;{SID}'

URL = ('{}/_apis/accesscontrollists/{}?token={}&api-version=5.0'
       .format(ARGS.organization, ARGS.namespaceId, TOKEN))
HEADERS = {
    'Content-Type': 'application/json',
}

try:
    RESPONSE = requests.get(URL, headers=HEADERS, auth=(ARGS.pat, ''))
    RESPONSE.raise_for_status()
except requests.exceptions.RequestException as err:
    print(f'##vso[task.logissue type=error] {err}')
    RESPONSE_TEXT = json.loads(RESPONSE.text)
    CODE = RESPONSE_TEXT['errorCode']
    MESSAGE = RESPONSE_TEXT['message']
    print(f'##vso[task.logissue type=error] Response code: {CODE}')
    print(f'##vso[task.logissue type=error] Response message: {MESSAGE}')
    sys.exit(1)
else:
    CURRENT_ACL = RESPONSE.json()['value'][0]['acesDictionary']
    print(f'[DEBUG] CURRENT_ACL= {CURRENT_ACL}')
    CURRENT_ALLOW = CURRENT_ACL.get(DESCRIPTOR)['allow']
    CURRENT_DENY = CURRENT_ACL.get(DESCRIPTOR)['deny']

    if CURRENT_ALLOW == int(ARGS.allow) and CURRENT_DENY == int(ARGS.deny):
        print('[INFO] Current permissions match desired')
    else:
        print('##vso[task.logissue type=error] Current permissions do not match desired')
        print(f'##vso[task.logissue type=error] Desired permissions = {ARGS.allow} / {ARGS.deny}')
        print(f'##vso[task.logissue type=error] Current permissions = {CURRENT_ALLOW} / {CURRENT_DENY}')
        sys.exit(1)
