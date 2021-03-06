"""
This script creates group in projct via Azure DevOps API
"""

import json
import argparse
import sys
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument("--organization", type=str, required=True)
PARSER.add_argument("--projectScopeDescriptor", type=str, required=True)
PARSER.add_argument("--groupName", type=str, required=True)
PARSER.add_argument("--groupDescription", type=str, required=True)
PARSER.add_argument("--pat", type=str, required=True)

ARGS = PARSER.parse_args()

print(f"[INFO] Creating {ARGS.groupName} group..")
URL = "{}/_apis/graph/groups?scopeDescriptor={}&api-version=5.0-preview.1".format(
    ARGS.organization, ARGS.projectScopeDescriptor
)
HEADERS = {
    "Content-Type": "application/json",
}

DATA = {"displayName": f"{ARGS.groupName}", "description": f"{ARGS.groupDescription}"}

try:
    RESPONSE = requests.post(
        URL, headers=HEADERS, data=json.dumps(DATA), auth=(ARGS.pat, "")
    )
    RESPONSE.raise_for_status()
except requests.exceptions.RequestException as err:
    print(f"##vso[task.logissue type=error] {err}")
    RESPONSE_TEXT = json.loads(RESPONSE.text)
    CODE = RESPONSE_TEXT["errorCode"]
    MESSAGE = RESPONSE_TEXT["message"]
    print(f"##vso[task.logissue type=error] Response code: {CODE}")
    print(f"##vso[task.logissue type=error] Response message: {MESSAGE}")
    sys.exit(1)
else:
    RESPONSE_CODE = RESPONSE.status_code
    if RESPONSE_CODE == 201:
        print(f"[INFO] Group {ARGS.groupName} has been created successfully")
    else:
        print(
            f"##vso[task.logissue type=error] Group {ARGS.groupName} has not been created"
        )
        sys.exit(1)
