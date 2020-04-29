"""
This script sets cross-repo Git policy
"""

import json
import argparse
import sys
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--organization', type=str, required=True)
PARSER.add_argument('--projectName', type=str, required=True)
PARSER.add_argument('--minApproverCount', type=str, required=True)
PARSER.add_argument('--pat', type=str, required=True)

ARGS = PARSER.parse_args()

URL = ('{}/{}/_apis/policy/configurations?api-version=5.1'
       .format(ARGS.organization, ARGS.projectName))
HEADERS = {
    'Content-Type': 'application/json',
}

NULL = None
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
                'repositoryId': NULL
            }
        ]
    }
}

try:
    RESPONSE = requests.post(URL, headers=HEADERS, data=json.dumps(DATA), auth=(ARGS.pat, ''))
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
    print('[INFO] Cross-repo Git policy has been set successfully')
