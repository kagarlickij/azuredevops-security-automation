"""
This script creates new Artifact feed
"""

import json
import argparse
import sys
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument("--organization", type=str, required=True)
PARSER.add_argument("--projectName", type=str)
PARSER.add_argument("--feedName", type=str, required=True)
PARSER.add_argument("--pat", type=str, required=True)

ARGS = PARSER.parse_args()

if not ARGS.projectName:
    print("[INFO] no projectName received, so working with on-prem API")
    URL = "{}/_apis/packaging/feeds?api-version=5.0-preview.1".format(ARGS.organization)
else:
    print("[INFO] projectName received, so working with cloud API")
    URL = "{}/{}/_apis/packaging/feeds?api-version=5.0-preview.1".format(
        ARGS.organization, ARGS.projectName
    )

HEADERS = {
    "Content-Type": "application/json",
}

DATA = {
    "name": f"{ARGS.feedName}",
    "upstreamEnabled": "false",
    "capabilities": "defaultCapabilities",
}

print(f"[INFO] Creating {ARGS.feedName} feed..")
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
        print(f"[INFO] Feed {ARGS.feedName} has been created successfully")
    else:
        print(
            f"##vso[task.logissue type=error] Feed {ARGS.feedName} has not been created"
        )
        sys.exit(1)
