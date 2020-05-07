"""
This script deletes group in projct via TFSSecurity cmd
"""

import subprocess
import argparse

PARSER = argparse.ArgumentParser()

PARSER.add_argument("--organization", type=str, required=True)
PARSER.add_argument("--projectName", type=str, required=True)
PARSER.add_argument("--groupName", type=str, required=True)

ARGS = PARSER.parse_args()

CMD = [
    "C:\\Program Files\\Azure DevOps Server 2019\\Tools\\TFSSecurity.exe",
    "/gd",
    f"[{ARGS.projectName}]\\{ARGS.groupName}",
    f"/collection:{ARGS.organization}",
]

DELETE_OUTPUT = subprocess.run(
    CMD, check=True, stdout=subprocess.PIPE, shell=True
).stdout.decode("utf-8")

print(f"[DEBUG] DELETE_OUTPUT: {DELETE_OUTPUT}")
