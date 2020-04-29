"""
This script gets current quantity of group members and compares it with desired
"""

import argparse
import sys

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--groupName', type=str, required=True)
PARSER.add_argument('--desiredMembersQuantity', type=str, required=True)

ARGS = PARSER.parse_args()

CURRENT_MEMBERS_FILE = open(f'{ARGS.groupName}_members.txt', "r")
CURRENT_MEMBERS_FILE_READ = CURRENT_MEMBERS_FILE.read()
CURRENT_MEMBERS_LINE = ""
for LINE in CURRENT_MEMBERS_FILE_READ.splitlines():
    if "member(s):" in LINE:
        CURRENT_MEMBERS_LINE = LINE
        break

if CURRENT_MEMBERS_LINE == "":
    CURRENT_MEMBERS_QUANTITY = "0"
else:
    CURRENT_MEMBERS_QUANTITY = CURRENT_MEMBERS_LINE.split(' ')[0]

print(f'[DEBUG] CURRENT_MEMBERS_QUANTITY: {CURRENT_MEMBERS_QUANTITY}')

if int(CURRENT_MEMBERS_QUANTITY) == int(ARGS.desiredMembersQuantity):
    print('[INFO] Current members quantity match desired')
else:
    print('##vso[task.logissue type=error] Current members quantity does not match desired')
    print(f'##vso[task.logissue type=error] Desired members quantity = {ARGS.desiredMembersQuantity}')
    print(f'##vso[task.logissue type=error] Current members quantity = {CURRENT_MEMBERS_QUANTITY}')
    print(f'##vso[task.logissue type=error] Current members = {CURRENT_MEMBERS_FILE_READ}')
    sys.exit(1)
