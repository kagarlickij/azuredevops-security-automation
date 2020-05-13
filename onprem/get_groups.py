"""
This script gets list of current groups and compares it with list of desired groups
"""

import subprocess
import argparse
import sys

PARSER = argparse.ArgumentParser()

PARSER.add_argument("--organization", type=str, required=True)
PARSER.add_argument("--projectId", type=str, required=True)
PARSER.add_argument("--desiredGroupsList", nargs="+", required=True)

ARGS = PARSER.parse_args()

CMD = [
    "C:\\Program Files\\Azure DevOps Server 2019\\Tools\\TFSSecurity.exe",
    "/g",
    f"vstfs:///Classification/TeamProject/{ARGS.projectId}",
    f"/collection:{ARGS.organization}",
]

LIST_GROUPS_OUTPUT = subprocess.run(
    CMD, check=True, stdout=subprocess.PIPE
).stdout.decode("utf-8")

CURRENT_GROUPS_LIST = list()
for LINE in LIST_GROUPS_OUTPUT.splitlines():
    if "Display name" in LINE:
        GROUP_NAME = LINE.split("\\")[1]
        CURRENT_GROUPS_LIST.append(GROUP_NAME)

print(f"[DEBUG] CURRENT_GROUPS_LIST: {CURRENT_GROUPS_LIST}")

DESIRED_GROUPS_LIST = ARGS.desiredGroupsList
DESIRED_GROUPS_LIST.sort()
CURRENT_GROUPS_LIST.sort()

if CURRENT_GROUPS_LIST == DESIRED_GROUPS_LIST:
    print("[INFO] Current list of groups match desired")
else:
    print(
        "##vso[task.logissue type=error] Current list of groups does not match desired"
    )
    print(f"##vso[task.logissue type=error] currentGroupsList = {CURRENT_GROUPS_LIST}")
    print(f"##vso[task.logissue type=error] desiredGroupsList = {DESIRED_GROUPS_LIST}")
    sys.exit(1)
