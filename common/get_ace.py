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
PARSER.add_argument('--groupAce', type=str)
PARSER.add_argument('--allow', type=str)
PARSER.add_argument('--deny', type=str)
PARSER.add_argument('--pat', type=str)

ARGS = PARSER.parse_args()

if not ARGS.projectId or not ARGS.groupName or not ARGS.groupAce or not ARGS.allow or not ARGS.deny or not ARGS.pat:
    print(f'[ERROR] missing required arguments')
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

ACE = (os.environ[(ARGS.groupAce).upper()])
FULL_ACE = f'Microsoft.TeamFoundation.Identity;{ACE}'

URL = '{}/_apis/accesscontrollists/{}?token={}&api-version=5.0'.format(ARGS.organization, ARGS.namespaceId, TOKEN)
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
    CURRENT_ACL = RESPONSE.json()['value'][0]['acesDictionary']
    CURRENT_ALLOW = CURRENT_ACL.get(FULL_ACE)['allow']
    CURRENT_DENY = CURRENT_ACL.get(FULL_ACE)['deny']

    if CURRENT_ALLOW == int(ARGS.allow) and CURRENT_DENY == int(ARGS.deny):
        print(f'[INFO] Current permissions match desired')
    else:
        print(f'[ERROR] Current permissions do not match desired')
        print(f'[ERROR] Desired permissions = {ARGS.allow} / {ARGS.deny}')
        print(f'[ERROR] Current permissions = {CURRENT_ALLOW} / {CURRENT_DENY}')
        sys.exit(1)
