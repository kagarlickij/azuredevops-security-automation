"""
This script gets list of current groups and compares it with list of desired groups
"""

import json
import argparse
import sys
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument("--organization", type=str, required=True)
PARSER.add_argument("--projectScopeDescriptor", type=str, required=True)
PARSER.add_argument("--desiredGroupsList", nargs="+", required=True)
PARSER.add_argument("--pat", type=str, required=True)

ARGS = PARSER.parse_args()

DESIRED_GROUPS_LIST = ARGS.desiredGroupsList

URL = "{}/_apis/graph/groups?scopeDescriptor={}&api-version=5.0-preview.1".format(
    ARGS.organization, ARGS.projectScopeDescriptor
)

HEADERS = {
    "Content-Type": "application/json",
}

try:
    RESPONSE = requests.get(URL, headers=HEADERS, auth=(ARGS.pat, ""))
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
    CURRENT_GROUPS_LIST = []
    GROUPS = RESPONSE.json()["value"]

    for GROUP in GROUPS:
        groupDisplayName = GROUP["displayName"]
        CURRENT_GROUPS_LIST.append(groupDisplayName)

    DESIRED_GROUPS_LIST.sort()
    CURRENT_GROUPS_LIST.sort()
    if CURRENT_GROUPS_LIST == DESIRED_GROUPS_LIST:
        print("[INFO] Current list of groups match desired")
    else:
        print(
            "##vso[task.logissue type=error] Current list of groups does not match desired"
        )
        print(
            f"##vso[task.logissue type=error] currentGroupsList = {CURRENT_GROUPS_LIST}"
        )
        print(
            f"##vso[task.logissue type=error] desiredGroupsList = {DESIRED_GROUPS_LIST}"
        )
        sys.exit(1)
