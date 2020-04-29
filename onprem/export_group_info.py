"""
This script gets and exports SID of the Azure DevOps group
"""

import argparse
import sys

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--groupName', type=str, required=True)
PARSER.add_argument('--groupSid', type=str, required=True)

ARGS = PARSER.parse_args()

LIST_GROUPS_OUTPUT = open('groups_list.txt', "r")
LIST_GROUPS_OUTPUT_READ = LIST_GROUPS_OUTPUT.read()
for LINE in LIST_GROUPS_OUTPUT_READ.splitlines():
    if "SID" in LINE:
        SID = LINE.split(': ')[1]
    if "Display name" in LINE:
        GROUP_NAME = LINE.split('\\')[1]
        if GROUP_NAME == ARGS.groupName:
            break

try:
    SID
except NameError:
    print(f'##vso[task.logissue type=error] Group {ARGS.groupName} was not found')
    sys.exit(1)
else:
    print(f'[INFO] Group {ARGS.groupName} SID = {SID}')
    print(f'##vso[task.setvariable variable={ARGS.groupSid}]{SID}')
