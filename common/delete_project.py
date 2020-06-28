"""
This script deletes Azure DevOps project
"""

import json
import argparse
import sys
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument("--organization", type=str, required=True)
PARSER.add_argument("--projectName", type=str, required=True)
PARSER.add_argument("--projectId", type=str, required=True)
PARSER.add_argument("--pat", type=str, required=True)

ARGS = PARSER.parse_args()

URL = "{}/_apis/projects/{}?api-version=5.0".format(ARGS.organization, ARGS.projectId)
HEADERS = {
    "Content-Type": "application/json",
}

try:
    RESPONSE = requests.delete(URL, headers=HEADERS, auth=(ARGS.pat, ""))
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
    if RESPONSE_CODE == 202:
        print(f"[INFO] Project {ARGS.projectName} has been deleted successfully")
    else:
        print(
            f"##vso[task.logissue type=error] Project {ARGS.projectName} has not been deleted"
        )
        sys.exit(1)
