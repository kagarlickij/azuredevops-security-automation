"""
This script creates temporary Release pipeline
"""

import json
import argparse
import sys
import requests

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--organization', type=str, required=True)
PARSER.add_argument('--projectName', type=str, required=True)
PARSER.add_argument('--pat', type=str, required=True)

ARGS = PARSER.parse_args()

print('[INFO] Creating tmp Release pipeline..')
URL = ('{}/{}/_apis/release/definitions?api-version=5.0'
       .format(ARGS.organization, ARGS.projectName))
HEADERS = {
    'Content-Type': 'application/json',
}

DATA = {
    'source': 'undefined',
    'revision': 1,
    'description': 'null',
    'createdBy': 'null',
    'createdOn': '0001-01-01T00:00:00',
    'modifiedBy': 'null',
    'modifiedOn': '0001-01-01T00:00:00',
    'isDeleted': 'false',
    'variables': {},
    'variableGroups': [],
    'environments': [
        {
            'id': 0,
            'name': 'Stage 1',
            'rank': 1,
            'variables': {},
            'variableGroups': [],
            'preDeployApprovals': {
                'approvals': [
                    {
                        'rank': 1,
                        'isAutomated': 'true',
                        'isNotificationOn': 'false',
                        'id': 1
                    }
                ],
                'approvalOptions': {
                    'requiredApproverCount': 'null',
                    'releaseCreatorCanBeApprover': 'false',
                    'autoTriggeredAndPreviousEnvironmentApprovedCanBeSkipped': 'false',
                    'enforceIdentityRevalidation': 'false',
                    'timeoutInMinutes': 0,
                    'executionOrder': 'beforeGates'
                }
            },
            'deployStep': {
                'id': 2
            },
            'postDeployApprovals': {
                'approvals': [
                    {
                        'rank': 1,
                        'isAutomated': 'true',
                        'isNotificationOn': 'false',
                        'id': 3
                    }
                ],
                'approvalOptions': {
                    'requiredApproverCount': 'null',
                    'releaseCreatorCanBeApprover': 'false',
                    'autoTriggeredAndPreviousEnvironmentApprovedCanBeSkipped': 'false',
                    'enforceIdentityRevalidation': 'false',
                    'timeoutInMinutes': 0,
                    'executionOrder': 'afterSuccessfulGates'
                }
            },
            'deployPhases': [
                {
                    'deploymentInput': {
                        'parallelExecution': {
                            'parallelExecutionType': 'none'
                        },
                        'timeoutInMinutes': 0,
                        'jobCancelTimeoutInMinutes': 1,
                        'condition': 'succeeded()',
                        'overrideInputs': {}
                    },
                    'rank': 1,
                    'phaseType': 'runOnServer',
                    'name': 'Agentless job',
                    'refName': 'null',
                    'workflowTasks': []
                }
            ],
            'environmentOptions': {
                'emailNotificationType': 'OnlyOnFailure',
                'emailRecipients': 'release.environment.owner;release.creator',
                'skipArtifactsDownload': 'false',
                'timeoutInMinutes': 0,
                'enableAccessToken': 'false',
                'publishDeploymentStatus': 'true',
                'badgeEnabled': 'false',
                'autoLinkWorkItems': 'false',
                'pullRequestDeploymentEnabled': 'false'
            },
            'demands': [],
            'conditions': [
                {
                    'name': 'ReleaseStarted',
                    'conditionType': 'event',
                    'value': ''
                }
            ],
            'executionPolicy': {
                'concurrencyCount': 1,
                'queueDepthCount': 0
            },
            'schedules': [],
            'retentionPolicy': {
                'daysToKeep': 30,
                'releasesToKeep': 3,
                'retainBuild': 'true'
            },
            'processParameters': {},
            'properties': {
                'BoardsEnvironmentType': {
                    '$type': 'System.String',
                    '$value': 'unmapped'
                },
                'LinkBoardsWorkItems': {
                    '$type': 'System.String',
                    '$value': 'False'
                }
            },
            'preDeploymentGates': {
                'id': 0,
                'gatesOptions': 'null',
                'gates': []
            },
            'postDeploymentGates': {
                'id': 0,
                'gatesOptions': 'null',
                'gates': []
            },
            'environmentTriggers': []
        }
    ],
    'artifacts': [],
    'triggers': [],
    'releaseNameFormat': 'Release-$(rev:r)',
    'tags': [],
    'properties': {
        'DefinitionCreationSource': {
            '$type': 'System.String',
            '$value': 'ReleaseNew'
        },
        'IntegrateBoardsWorkItems': {
            '$type': 'System.String',
            '$value': 'False'
        },
        'IntegrateJiraWorkItems': {
            '$type': 'System.String',
            '$value': 'false'
        }
    },
    'name': 'tmp',
    'path': '\\',
    'projectReference': 'null',
    '_links': {}
}

try:
    RESPONSE = requests.post(URL, headers=HEADERS, data=json.dumps(DATA), auth=(ARGS.pat, ''))
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
    RESPONSE_CODE = RESPONSE.status_code
    if RESPONSE_CODE == 200:
        print('[INFO] tmp Release pipeline has been created successfully')
    else:
        print('##vso[task.logissue type=error] tmp Release pipeline has not been created')
        sys.exit(1)
