"""
This script sets ACL for Artifact feed
"""

import json
import argparse
import sys
import os
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument("--organization", type=str, required=True)
PARSER.add_argument("--feedId", type=str, required=True)
PARSER.add_argument("--projectName", type=str)
PARSER.add_argument("--groupName", type=str, required=True)
PARSER.add_argument("--groupSid", type=str, required=True)
PARSER.add_argument("--role", type=str, required=True)
PARSER.add_argument("--pat", type=str, required=True)

ARGS = PARSER.parse_args()

SID = os.environ[(ARGS.groupSid).upper()]

if not ARGS.projectName:
    print("[INFO] no projectName received, so working with on-prem API")
    URL = "{}/_apis/packaging/Feeds/{}/permissions?api-version=5.0-preview.1".format(
        ARGS.organization, ARGS.feedId
    )
else:
    print("[INFO] projectName received, so working with cloud API")
    URL = "{}/{}/_apis/packaging/Feeds/{}/permissions?api-version=5.0-preview.1".format(
        ARGS.organization, ARGS.projectName, ARGS.feedId
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
    CURRENT_ACL = RESPONSE.json()
    ACCESS_DICT = CURRENT_ACL["value"][0]

    ACE = {
        "role": f"{ARGS.role}",
        "identityDescriptor": f"Microsoft.TeamFoundation.Identity;{SID}",
        "displayName": "None",
        "isInheritedRole": "False",
    }

    DESIRED_ACL = [ACE]

    print(f"[INFO] Setting permissions for {ARGS.groupName} group..")
    try:
        RESPONSE = requests.patch(
            URL, headers=HEADERS, data=json.dumps(DESIRED_ACL), auth=(ARGS.pat, "")
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
        if RESPONSE_CODE == 200:
            print(
                f"[INFO] Permissions for {ARGS.groupName} group have been set successfully"
            )
        else:
            print(
                f"##vso[task.logissue type=error] Permissions for {ARGS.groupName} group have not been set successfully"
            )
            sys.exit(1)
