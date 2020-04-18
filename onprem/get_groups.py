import argparse
import sys

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--desiredGroupsList', nargs='+')

ARGS = PARSER.parse_args()

if not ARGS.desiredGroupsList:
    print(f'[ERROR] missing required arguments')
    sys.exit(1)

DESIRED_GROUPS_LIST = ARGS.desiredGroupsList

LIST_GROUPS_OUTPUT = open('list_groups_output.txt', "r")
LIST_GROUPS_OUTPUT_READ = LIST_GROUPS_OUTPUT.read()
CURRENT_GROUPS_LIST = list()
for LINE in LIST_GROUPS_OUTPUT_READ.splitlines():
    if "Display name" in LINE:
        GROUP_NAME = LINE.split('\\')[1]
        CURRENT_GROUPS_LIST.append(GROUP_NAME)

print(f'[DEBUG] CURRENT_GROUPS_LIST: {CURRENT_GROUPS_LIST}')

DESIRED_GROUPS_LIST.sort()
CURRENT_GROUPS_LIST.sort()

if CURRENT_GROUPS_LIST == DESIRED_GROUPS_LIST:
    print(f'[INFO] Current list of groups match desired')
else:
    print(f'[ERROR] Current list of groups does not match desired')
    print(f'[ERROR] currentGroupsList = {CURRENT_GROUPS_LIST}')
    print(f'[ERROR] desiredGroupsList = {DESIRED_GROUPS_LIST}')
    sys.exit(1)