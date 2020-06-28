"""
This script generates pylint badge that is used in README.md
"""

import subprocess
import sys
import json
import argparse
import os
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument("--gistId", type=str, required=True)
PARSER.add_argument("--gitHubPat", type=str, required=True)

ARGS = PARSER.parse_args()

PYLINT_CMD = ["pylint --exit-zero ./**/*.py"]

PYLINT_OUTPUT = subprocess.run(
    PYLINT_CMD, check=True, stdout=subprocess.PIPE, shell=True
).stdout.decode("utf-8")
PYLINT_SCORE = PYLINT_OUTPUT.split("at ", 1)[1].split("/", 1)[0]
print(f"[INFO] PYLINT_SCORE: {PYLINT_SCORE}")

ANYBADGE_CMD = [
    "anybadge",
    "--overwrite",
    "--label",
    "pylint",
    "--value",
    f"{PYLINT_SCORE}",
    "--file",
    "pylint.svg",
    "2=red",
    "4=orange",
    "8=yellow",
    "10=green",
]

subprocess.run(ANYBADGE_CMD, check=True, stdout=subprocess.PIPE).stdout.decode("utf-8")

SVG = open("pylint.svg", "r")
SVG_READ = SVG.read()

URL = "https://api.github.com/gists/{}".format(ARGS.gistId)
HEADERS = {"Authorization": f"token {ARGS.gitHubPat}"}
DATA = {
    "description": "Created via API",
    "files": {"pylint.svg": {"content": f"{SVG_READ}"}},
}

try:
    RESPONSE = requests.patch(URL, headers=HEADERS, data=json.dumps(DATA))
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
    print("[INFO] SVG badge has been pushed to Gist successfully")

os.remove("pylint.svg")
