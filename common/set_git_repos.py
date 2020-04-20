import json
import argparse
import sys
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--organization', type=str)
PARSER.add_argument('--projectName', type=str)
PARSER.add_argument('--minApproverCount', type=str)
PARSER.add_argument('--pat', type=str)

ARGS = PARSER.parse_args()

if not ARGS.organization or not ARGS.projectName or not ARGS.minApproverCount or not ARGS.pat:
    print(f'[ERROR] missing required arguments')
    sys.exit(1)

URL = '{}/{}/_apis/policy/configurations?api-version=5.1'.format(ARGS.organization, ARGS.projectName)
HEADERS = {
    'Content-Type': 'application/json',
}

null = None
DATA = {
    'isEnabled': 'true',
    'isBlocking': 'true',
    'type': {
        'id': 'fa4e907d-c16b-4a4c-9dfa-4906e5d171dd'
    },
    'settings': {
        'minimumApproverCount': f'{ARGS.minApproverCount}',
        'creatorVoteCounts': 'false',
        'scope': [
            {
                'refName': 'refs/heads/master',
                'matchKind': 'exact',
                'repositoryId': null
            }
        ]
    }
}

try:
    RESPONSE = requests.post(URL, headers=HEADERS, data=json.dumps(DATA), auth=(ARGS.pat,''))
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
    print(RESPONSE)
