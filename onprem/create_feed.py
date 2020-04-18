import json
import argparse
import sys
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--organization', type=str, default='https://ados.demo.kagarlickij.com/DefaultCollection')
PARSER.add_argument('--feedName', type=str)
PARSER.add_argument('--pat', type=str)

ARGS = PARSER.parse_args()

if not ARGS.feedName or not ARGS.pat:
    print(f'[ERROR] missing required arguments')
    sys.exit(1)

print(f'[INFO] Creating {ARGS.feedName} feed..')
URL = '{}/_apis/packaging/feeds?api-version=5.0-preview.1'.format(ARGS.organization)
HEADERS = {
    'Content-Type': 'application/json',
}

DATA = {
    'name': f'{ARGS.feedName}',
    'upstreamEnabled': 'false',
    'capabilities': 'defaultCapabilities'
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
    RESPONSE_CODE = RESPONSE.status_code
    if RESPONSE_CODE == 201:
        print(f'[INFO] Feed {ARGS.feedName} has been created successfully')
    else:
        print(f'[ERROR] Feed {ARGS.feedName} has not been created')
        sys.exit(1)
