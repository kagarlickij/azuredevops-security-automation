"""
This script creates group in projct via TFSSecurity cmd
"""

import subprocess
import argparse

PARSER = argparse.ArgumentParser()

PARSER.add_argument("--organization", type=str, required=True)
PARSER.add_argument("--projectId", type=str, required=True)
PARSER.add_argument("--groupName", type=str, required=True)
PARSER.add_argument("--groupDescription", type=str, required=True)

ARGS = PARSER.parse_args()

CMD = [
    "C:\\Program Files\\Azure DevOps Server 2019\\Tools\\TFSSecurity.exe",
    "/gc",
    f"vstfs:///Classification/TeamProject/{ARGS.projectId}",
    f"{ARGS.groupName}",
    f"{ARGS.groupDescription}",
    f"/collection:{ARGS.organization}",
]

CREATE_OUTPUT = subprocess.run(
    CMD, check=True, stdout=subprocess.PIPE, shell=True
).stdout.decode("utf-8")

print(f"[DEBUG] CREATE_OUTPUT: {CREATE_OUTPUT}")
