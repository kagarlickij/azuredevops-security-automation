import json
import argparse
import sys
from datetime import date
from datetime import datetime
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--organization', type=str)
PARSER.add_argument('--projectName', type=str)
PARSER.add_argument('--pat', type=str)

ARGS = PARSER.parse_args()

if not ARGS.projectName or not ARGS.pat:
    print(f'[ERROR] missing required arguments')
    sys.exit(1)

HEADERS = {
    'Content-Type': 'application/json',
}

URL = '{}/{}/_apis/git/repositories?api-version=5.0'.format(ARGS.organization, ARGS.projectName)

with open('./common/excluded_repos.txt') as text_file:
    EXCLUDED_REPOS = text_file.read().splitlines()
print(f'[INFO] Excluded repos: {EXCLUDED_REPOS}')

ERROR_COUNTER = list()

try:
    RESPONSE = requests.get(URL, headers=HEADERS, auth=(ARGS.pat,''))
    RESPONSE.raise_for_status()
except Exception as err:
    print(f'[ERROR] {err}')
    RESPONSE_TEXT = json.loads(RESPONSE.text)
    CODE = RESPONSE_TEXT['errorCode']
    MESSAGE = RESPONSE_TEXT['message']
    print(f'[ERROR] Response code: {CODE}')
    print(f'[ERROR] Response message: {MESSAGE}')
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
            date_format = '%Y-%m-%d'

            URL = '{}/{}/_apis/git/repositories/{}/refs?api-version=5.0'.format(ARGS.organization, ARGS.projectName, REPO_ID)
            HEADERS = {
                'Content-Type': 'application/json',
            }

            try:
                RESPONSE = requests.get(URL, headers=HEADERS, auth=(ARGS.pat,''))
                RESPONSE.raise_for_status()
            except Exception as err:
                print(f'[ERROR] {err}')
                RESPONSE_TEXT = json.loads(RESPONSE.text)
                CODE = RESPONSE_TEXT['errorCode']
                MESSAGE = RESPONSE_TEXT['message']
                print(f'[ERROR] Response code: {CODE}')
                print(f'[ERROR] Response message: {MESSAGE}')
                sys.exit(1)
            else:
                BRANCHES = RESPONSE.json()['value']

                UNKNOWN_BRANCHES = list()
                OUTDATED_BRANCHES = list()
                OUTDATED_PRS = list()
                MASTER_POLICIES_QUANTITY = ''

                for BRANCH in BRANCHES:
                    BRANCH_NAME = BRANCH['name']
                    BRANCH_SHORTNAME = BRANCH_NAME.replace('refs/heads/', '')
                    if BRANCH_SHORTNAME == 'master':
                        URL = '{}/{}/_apis/git/policy/configurations?REPO_ID={}&refName={}&api-version=5.0-preview.1'.format(ARGS.organization, ARGS.projectName, REPO_ID, BRANCH_NAME)
                        try:
                            RESPONSE = requests.get(URL, headers=HEADERS, auth=(ARGS.pat,''))
                            RESPONSE.raise_for_status()
                        except Exception as err:
                            print(f'[ERROR] {err}')
                            RESPONSE_TEXT = json.loads(RESPONSE.text)
                            CODE = RESPONSE_TEXT['errorCode']
                            MESSAGE = RESPONSE_TEXT['message']
                            print(f'[ERROR] Response code: {CODE}')
                            print(f'[ERROR] Response message: {MESSAGE}')
                            sys.exit(1)
                        else:
                            POLICY_COUNTER = RESPONSE.json()['count']
                            MASTER_POLICIES_QUANTITY = int(POLICY_COUNTER)

                    elif ('feature/' in BRANCH_SHORTNAME or 'bugfix/' in BRANCH_SHORTNAME):
                        URL = '{}/_apis/git/repositories/{}/commits?searchCriteria.itemVersion.version={}&api-version=5.0'.format(ARGS.organization, ARGS.projectName, BRANCH_SHORTNAME)
                        try:
                            RESPONSE = requests.get(URL, headers=HEADERS, auth=(ARGS.pat,''))
                            RESPONSE.raise_for_status()
                        except Exception as err:
                            print(f'[ERROR] {err}')
                            RESPONSE_TEXT = json.loads(RESPONSE.text)
                            CODE = RESPONSE_TEXT['errorCode']
                            MESSAGE = RESPONSE_TEXT['message']
                            print(f'[ERROR] Response code: {CODE}')
                            print(f'[ERROR] Response message: {MESSAGE}')
                            sys.exit(1)
                        else:
                            LATEST_COMMIT_ID = RESPONSE.json()['value'][0]['commitId']
                            LATEST_COMMIT_DATE = RESPONSE.json()['value'][0]['committer']['date']
                            LATEST_COMMIT_SHORT_DATE = LATEST_COMMIT_DATE.split('T')[0]
                            LATEST_COMMIT_SHORT_DATE_TIME = datetime.strptime(LATEST_COMMIT_SHORT_DATE, date_format)
                            CURRENT_DATE = date.today().strftime('%Y-%m-%d')
                            CURRENT_DATE_TIME = datetime.strptime(CURRENT_DATE, date_format)
                            LATEST_COMMIT_AGE = CURRENT_DATE_TIME - LATEST_COMMIT_SHORT_DATE_TIME
                            if int(LATEST_COMMIT_AGE.days) > 10:
                                print(f'[ERROR] Latest commit {LATEST_COMMIT_ID} is too old: {LATEST_COMMIT_AGE.days} day(s)')
                                OUTDATED_BRANCHES.append(BRANCH_SHORTNAME)
                            else:
                                pass

                    elif 'refs/tags/v' in BRANCH_NAME:
                        pass

                    elif 'refs/pull/' in BRANCH_NAME:
                        pass

                    else:
                        UNKNOWN_BRANCHES.append(BRANCH_NAME)


                URL = '{}/{}/_apis/git/repositories/{}/pullrequests?api-version=5.0'.format(ARGS.organization, ARGS.projectName, REPO_ID)
                try:
                    RESPONSE = requests.get(URL, headers=HEADERS, auth=(ARGS.pat,''))
                    RESPONSE.raise_for_status()
                except Exception as err:
                    print(f'[ERROR] {err}')
                    RESPONSE_TEXT = json.loads(RESPONSE.text)
                    CODE = RESPONSE_TEXT['errorCode']
                    MESSAGE = RESPONSE_TEXT['message']
                    print(f'[ERROR] Response code: {CODE}')
                    print(f'[ERROR] Response message: {MESSAGE}')
                    sys.exit(1)
                else:
                    PRS = RESPONSE.json()['value']
                    for PR in PRS:
                        PR_ID = PR['pullRequestId']
                        PR_DATE = PR['creationDate']
                        PR_SHORT_DATE = PR_DATE.split('T')[0]
                        PR_SHORT_DATE_TIME = datetime.strptime(PR_SHORT_DATE, date_format)
                        CURRENT_DATE = date.today().strftime('%Y-%m-%d')
                        CURRENT_DATE_TIME = datetime.strptime(CURRENT_DATE, date_format)
                        PR_AGE = CURRENT_DATE_TIME - PR_SHORT_DATE_TIME
                        if int(PR_AGE.days) > 10:
                            OUTDATED_PRS.append(PR_ID)
                        else:
                            pass

                if len(UNKNOWN_BRANCHES) == 0:
                    print(f'[INFO] All branch names follow standard')
                else:
                    print(f'##vso[task.logissue type=warning] Branch names that do not follow standard: {UNKNOWN_BRANCHES}')

                if len(OUTDATED_BRANCHES) == 0:
                    print(f'[INFO] All branches are up to date')
                else:
                    print(f'##vso[task.logissue type=warning] Outdated branches: {OUTDATED_BRANCHES}')

                if len(OUTDATED_PRS) == 0:
                    print(f'[INFO] All Pull requests are up to date')
                else:
                    print(f'##vso[task.logissue type=warning] Outdated Pull requests: {OUTDATED_PRS}')

                if MASTER_POLICIES_QUANTITY != '':
                    print(f'[INFO] master branch has {MASTER_POLICIES_QUANTITY} policy(es) assigned')
                else:
                    print(f'[ERROR] master branch does not have policies assigned')
                    ERROR_COUNTER.append(REPO_ID)

if len(ERROR_COUNTER) != 0:
    sys.exit(1)
