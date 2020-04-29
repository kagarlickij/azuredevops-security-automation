"""
This script checks if all git repos in project follow best practices
"""

import json
import argparse
import sys
from datetime import date
from datetime import datetime
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--organization', type=str, required=True)
PARSER.add_argument('--projectName', type=str, required=True)
PARSER.add_argument('--maxCommitAge', type=str, required=True)
PARSER.add_argument('--maxPullRequestAge', type=str, required=True)
PARSER.add_argument('--minApproverCount', type=str, required=True)
PARSER.add_argument('--pat', type=str, required=True)

ARGS = PARSER.parse_args()

HEADERS = {
    'Content-Type': 'application/json',
}

URL = ('{}/{}/_apis/git/repositories?api-version=5.0'
       .format(ARGS.organization, ARGS.projectName))

with open('./common/excluded_repos.txt') as text_file:
    EXCLUDED_REPOS = text_file.read().splitlines()
print(f'[INFO] Excluded repos: {EXCLUDED_REPOS}')

ERROR_COUNTER = list()

try:
    RESPONSE = requests.get(URL, headers=HEADERS, auth=(ARGS.pat, ''))
    RESPONSE.raise_for_status()
except requests.exceptions.RequestException as err:
    print(f'##vso[task.logissue type=error] {err}')
    RESPONSE_TEXT = json.loads(RESPONSE.text)
    CODE = RESPONSE_TEXT['errorCode']
    MESSAGE = RESPONSE_TEXT['message']
    print(f'##vso[task.logissue type=error] Response code: {CODE}')
    print(f'##vso[task.logissue type=error] Response message: {MESSAGE}')
    sys.exit(1)
else:
    REPOS = RESPONSE.json()['value']
    for REPO in REPOS:
        REPO_NAME = {REPO['name']}
        print(f'\n[INFO] Checking {REPO_NAME} repo..')
        REPO_ID = REPO['id']
        if REPO['name'] in EXCLUDED_REPOS:
            print(f'[INFO] Repo {REPO_NAME} is excluded')
        else:
            DATE_FORMAT = '%Y-%m-%d'

            URL = ('{}/{}/_apis/git/repositories/{}/refs?api-version=5.0'
                   .format(ARGS.organization, ARGS.projectName, REPO_ID))
            HEADERS = {
                'Content-Type': 'application/json',
            }

            try:
                RESPONSE = requests.get(URL, headers=HEADERS, auth=(ARGS.pat, ''))
                RESPONSE.raise_for_status()
            except requests.exceptions.RequestException as err:
                print(f'##vso[task.logissue type=error] {err}')
                RESPONSE_TEXT = json.loads(RESPONSE.text)
                CODE = RESPONSE_TEXT['errorCode']
                MESSAGE = RESPONSE_TEXT['message']
                print(f'##vso[task.logissue type=error] Response code: {CODE}')
                print(f'##vso[task.logissue type=error] Response message: {MESSAGE}')
                sys.exit(1)
            else:
                BRANCHES = RESPONSE.json()['value']

                UNKNOWN_BRANCHES = list()
                OUTDATED_BRANCHES = list()
                OUTDATED_PRS = list()

                for BRANCH in BRANCHES:
                    BRANCH_NAME = BRANCH['name']
                    BRANCH_SHORTNAME = BRANCH_NAME.replace('refs/heads/', '')
                    if ('feature/' in BRANCH_SHORTNAME or 'bugfix/' in BRANCH_SHORTNAME):
                        URL = ('{}/_apis/git/repositories/{}/commits?searchCriteria.itemVersion.version={}&api-version=5.0'
                               .format(ARGS.organization, REPO_ID, BRANCH_SHORTNAME))
                        try:
                            RESPONSE = requests.get(URL, headers=HEADERS, auth=(ARGS.pat, ''))
                            RESPONSE.raise_for_status()
                        except requests.exceptions.RequestException as err:
                            print(f'##vso[task.logissue type=error] {err}')
                            RESPONSE_TEXT = json.loads(RESPONSE.text)
                            CODE = RESPONSE_TEXT['errorCode']
                            MESSAGE = RESPONSE_TEXT['message']
                            print(f'##vso[task.logissue type=error] Response code: {CODE}')
                            print(f'##vso[task.logissue type=error] Response message: {MESSAGE}')
                            sys.exit(1)
                        else:
                            LATEST_COMMIT_ID = RESPONSE.json()['value'][0]['commitId']
                            LATEST_COMMIT_DATE = RESPONSE.json()['value'][0]['committer']['date']
                            LATEST_COMMIT_SHORT_DATE = LATEST_COMMIT_DATE.split('T')[0]
                            LATEST_COMMIT_SHORT_DATE_TIME = datetime.strptime(LATEST_COMMIT_SHORT_DATE, DATE_FORMAT)
                            CURRENT_DATE = date.today().strftime('%Y-%m-%d')
                            CURRENT_DATE_TIME = datetime.strptime(CURRENT_DATE, DATE_FORMAT)
                            LATEST_COMMIT_AGE = CURRENT_DATE_TIME - LATEST_COMMIT_SHORT_DATE_TIME
                            if int(LATEST_COMMIT_AGE.days) > int(ARGS.maxCommitAge):
                                print(f'##vso[task.logissue type=error] Latest commit {LATEST_COMMIT_ID} is too old: {LATEST_COMMIT_AGE.days} day(s)')
                                OUTDATED_BRANCHES.append(BRANCH_SHORTNAME)
                            else:
                                pass

                    elif BRANCH_SHORTNAME == 'master':
                        pass

                    elif 'refs/tags/v' in BRANCH_NAME:
                        pass

                    elif 'refs/pull/' in BRANCH_NAME:
                        pass

                    else:
                        UNKNOWN_BRANCHES.append(BRANCH_NAME)


                URL = ('{}/{}/_apis/git/repositories/{}/pullrequests?api-version=5.0'
                       .format(ARGS.organization, ARGS.projectName, REPO_ID))
                try:
                    RESPONSE = requests.get(URL, headers=HEADERS, auth=(ARGS.pat, ''))
                    RESPONSE.raise_for_status()
                except requests.exceptions.RequestException as err:
                    print(f'##vso[task.logissue type=error] {err}')
                    RESPONSE_TEXT = json.loads(RESPONSE.text)
                    CODE = RESPONSE_TEXT['errorCode']
                    MESSAGE = RESPONSE_TEXT['message']
                    print(f'##vso[task.logissue type=error] Response code: {CODE}')
                    print(f'##vso[task.logissue type=error] Response message: {MESSAGE}')
                    sys.exit(1)
                else:
                    PRS = RESPONSE.json()['value']
                    for PR in PRS:
                        PR_ID = PR['pullRequestId']
                        PR_DRAFT_STATUS = PR['isDraft']
                        if not PR_DRAFT_STATUS: # Don't need to check Draft PRs
                            PR_DATE = PR['creationDate']
                            PR_SHORT_DATE = PR_DATE.split('T')[0]
                            PR_SHORT_DATE_TIME = datetime.strptime(PR_SHORT_DATE, DATE_FORMAT)
                            CURRENT_DATE = date.today().strftime('%Y-%m-%d')
                            CURRENT_DATE_TIME = datetime.strptime(CURRENT_DATE, DATE_FORMAT)
                            PR_AGE = CURRENT_DATE_TIME - PR_SHORT_DATE_TIME
                            if int(PR_AGE.days) > int(ARGS.maxPullRequestAge):
                                OUTDATED_PRS.append(PR_ID)
                            else:
                                pass
                        else:
                            pass

                if len(UNKNOWN_BRANCHES) == 0:
                    print('[INFO] All branch names follow standard')
                else:
                    print(f'##vso[task.logissue type=warning] Branch names that do not follow standard: {UNKNOWN_BRANCHES}')

                if len(OUTDATED_BRANCHES) == 0:
                    print('[INFO] All branches are up to date')
                else:
                    print(f'##vso[task.logissue type=warning] Outdated branches: {OUTDATED_BRANCHES}')

                if len(OUTDATED_PRS) == 0:
                    print('[INFO] All Pull requests are up to date')
                else:
                    print(f'##vso[task.logissue type=warning] Outdated Pull requests: {OUTDATED_PRS}')


URL = ('{}/{}/_apis/policy/configurations?api-version=5.1'
       .format(ARGS.organization, ARGS.projectName))
HEADERS = {
    'Content-Type': 'application/json',
}

try:
    RESPONSE = requests.get(URL, headers=HEADERS, auth=(ARGS.pat, ''))
    RESPONSE.raise_for_status()
except requests.exceptions.RequestException as err:
    print(f'##vso[task.logissue type=error] {err}')
    RESPONSE_TEXT = json.loads(RESPONSE.text)
    CODE = RESPONSE_TEXT['errorCode']
    MESSAGE = RESPONSE_TEXT['message']
    print(f'##vso[task.logissue type=error] Response code: {CODE}')
    print(f'##vso[task.logissue type=error] Response message: {MESSAGE}')
    sys.exit(1)
else:
    BRANCH_POLICY_COUNT = RESPONSE.json()['count']
    if int(BRANCH_POLICY_COUNT) > 0:
        MATCH_KIND = RESPONSE.json()['value'][0]['settings']['scope'][0]['matchKind']
        REPO_ID = RESPONSE.json()['value'][0]['settings']['scope'][0]['repositoryId']
        APPROVERS_COUNT = RESPONSE.json()['value'][0]['settings']['minimumApproverCount']
        if MATCH_KIND == "Exact" and REPO_ID is None and APPROVERS_COUNT >= int(ARGS.minApproverCount):
            print(f'[INFO] default branch has reviewers policy assigned, minimum number of reviewers is {APPROVERS_COUNT}')
        else:
            print('##vso[task.logissue type=error] default branch does not have valid reviewers policy assigned')
            print(f'[DEBUG] MATCH_KIND = {MATCH_KIND}')
            print(f'[DEBUG] REPO_ID = {REPO_ID}')
            print(f'[DEBUG] APPROVERS_COUNT = {APPROVERS_COUNT}')
            sys.exit(1)
    else:
        print('##vso[task.logissue type=error] default branch does not have policies assigned')
        sys.exit(1)
