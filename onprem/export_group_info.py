import argparse
import sys

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--groupName', type=str)
PARSER.add_argument('--groupAce', type=str)

ARGS = PARSER.parse_args()

if not ARGS.groupName or not ARGS.groupAce:
    print(f'##vso[task.logissue type=error] missing required arguments')
    sys.exit(1)

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
    print(f'[INFO] Group {ARGS.groupName} ACE = {SID}')
    print(f'##vso[task.setvariable variable={ARGS.groupAce}]{SID}')
