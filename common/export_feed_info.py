"""
This script exports Feed ID
"""

import json
import argparse
import sys
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument("--organization", type=str, required=True)
PARSER.add_argument("--feedName", type=str, required=True)
PARSER.add_argument("--pat", type=str, required=True)

ARGS = PARSER.parse_args()

URL = "{}/_apis/packaging/feeds?api-version=5.0-preview.1".format(ARGS.organization)

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
    FEEDS = RESPONSE.json()["value"]

    for FEED in FEEDS:
        if FEED["name"] == ARGS.feedName:
            FEED_ID = FEED["id"]
            break

    try:
        FEED_ID
    except NameError:
        print(f"##vso[task.logissue type=error] Feed {ARGS.feedName} was not found")
        sys.exit(1)
    else:
        print(f"[INFO] Feed {ARGS.feedName} ID = {FEED_ID}")
        print(f"##vso[task.setvariable variable=feedId]{FEED_ID}")
