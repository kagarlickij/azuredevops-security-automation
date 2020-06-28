| Create project status | Check project status | pylint Score | License |
| ------------- | ------------- | ------------- | ------------- |
| [![Create project status](https://dev.azure.com/kagarlickij/azuredevops-security-automation/_apis/build/status/create?branchName=master)](https://dev.azure.com/kagarlickij/azuredevops-security-automation/_build/latest?definitionId=80&branchName=master) | [![Check project status](https://dev.azure.com/kagarlickij/azuredevops-security-automation/_apis/build/status/check?branchName=master)](https://dev.azure.com/kagarlickij/azuredevops-security-automation/_build/latest?definitionId=72&branchName=master) | ![pylint Score](https://gist.githubusercontent.com/kagarlickij/780fabe68201e08c8f2151ad02898bad/raw/pylint.svg) | [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.md) |

# Table of Contents
* [Challenge](#Challenge)
* [Solution](#Solution)
* [HLD diagram](#HLD-diagram)
* [How-to use](#How-to-use)
* [Azure DevOps APIs](#Azure-DevOps-APIs)
	* [Azure DevOps UI vs API naming](#Azure-DevOps-UI-vs-API-naming)
	* [Azure DevOps APIs and Versions](#Azure-DevOps-APIs-and-Versions)
	* [Personal vs System access token](#Personal-vs-System-access-token)
	* [Azure DevOps API throttling](#Azure-DevOps-API-throttling)
	* [Response codes](#Response-codes)
	* [Organization](#Organization)
	* [Project scope descriptor vs Project ID](#Project-scope-descriptor-vs-Project-ID)
	* [Tokens](#Tokens)
	* [Security namespaces](#Security-namespaces)
* [Azure DevOps Security basics](#Azure-DevOps-Security-basics)
	* [Numbers for permissions](#Numbers-for-permissions)
	* [Create entity vs set permissions](#Create-entity-vs-set-permissions)
* [Azure DevOps Artifact feeds](#Azure-DevOps-Artifact-feeds)
	* [Artifact feed name is still "busy" after feed is deleted](#Artifact-feed-name-is-still-"busy"-after-feed-is-deleted)
* [`create-project` pipeline](#`create-project`-pipeline)
* [`check-project` pipeline](#`check-project`-pipeline)
* [Pipelines execution](#Pipelines-execution)
	* [Triggers](#Triggers)
	* [Variables](#Variables)
	* [Azure DevOps specific syntax in scripts](#Azure-DevOps-specific-syntax-in-scripts)
* [Contribution](#Contribution)
	* [pre-commit and pre-push hooks](#pre-commit-and-pre-push-hooks)
	* [Pull request validation:](#Pull-request-validation:)
	* [Build](#Build)
* [Known issues](#Known-issues)

# Challenge
Azure DevOps gives a nice opportunity to have dedicated projects for dedicated teams and/or projects  
However default groups and permissions are too open for enterprise projects and too hard to understand for new Azure DevOps users  
Typically it ends with the whole team using administrator permissions  

# Solution
Create common groups and set relevant permissions to keep Azure DevOps users happy  
To keep enterprise security folks happy too setup security monitoring to ensure that nobody violates rules  
And to keep operations happy, both projects creation and verification is automated using Azure DevOps API and Pipelines  

# HLD diagram
![diagram](diagram.png)

# How-to use
1. Fork this repo
2. Put name of the new project name to `projectName` variable in [./cloud/create-project.yml](./cloud/create-project.yml) & [./cloud/check-project.yml](./cloud/check-project.yml) for Cloud and [./onprem/create-project.yml](./onprem/create-project.yml) & [./onprem/check-project.yml](./onprem/check-project.yml) for on-premise
3. Clone or create new Variable groups - `ados-group-names-$projectName` and `ados-acls-$projectName`
4. If you cloned Variable groups ensure that you're happy with values - **Variable groups keys and values are described in detail below**
5. Put cloned Variable group names to [./cloud/create-project.yml](./cloud/create-project.yml) & [./cloud/check-project.yml](./cloud/check-project.yml) for Cloud and [./onprem/create-project.yml](./onprem/create-project.yml) & [./onprem/check-project.yml](./onprem/check-project.yml) for on-premise
6. Create new Azure DevOps pipeline using [./cloud/create-project.yml](./cloud/create-project.yml) for Cloud and [./onprem/create-project.yml](./onprem/create-project.yml) for on-premise, rename pipeline (e.g. `create-$projectName`), run it and check logs
7. Create new Azure DevOps pipeline using [./cloud/check-project.yml](./cloud/check-project.yml) for Cloud and [./onprem/check-project.yml](./onprem/check-project.yml) for on-premise, rename pipeline (e.g. `check-$projectName`), run it and check logs

# Azure DevOps APIs
## Azure DevOps UI vs API naming
In Azure DevOps UI naming is different from API naming, e.g. in Artifact feed UI role is called "Owner" and API name is "administrator": [screenshot](https://prnt.sc/rq78ye)

## Azure DevOps APIs and Versions
Azure DevOps has a few APIs and each API has a few versions, e.g.:  
regular `https://dev.azure.com/{organization}/_apis/projects?api-version=5.0` to create Project,  
new `https://vssps.dev.azure.com/{organization}/_apis/graph/groups?scopeDescriptor={projectScopeDescriptor}&api-version=5.0-preview.1` to create Group

Here's summary of scripts vs used APIs (actions should be understandable from script names):  
`https://dev.azure.com` version `5.0` (can be switched to `5.1` if necessary):
1. [./common/create_project](./common/create_project.py)
2. [./common/check_permissions](./common/check_permissions.py)
3. [./common/set_permissions](./common/set_permissions.py)
4. [./common/check_git_policy](./common/check_git_policy.py)
5. [./common/set_git_policy](./common/set_git_policy.py)
6. [./cloud/export_project_info](./cloud/export_project_info.py)  

For on-premise link will be `server_url/collection`, e.g. `https://ados.demo.kagarlickij.com/DefaultCollection`  

`https://vssps.dev.azure.com` version `5.0-preview.1` vs TFSSecurity CLI:
1. [./cloud/export_project_info](./cloud/export_project_info.py)
2. [./cloud/get_group_members](./cloud/get_group_members.py)
3. [./cloud/get_groups](./cloud/get_groups.py)
4. [./cloud/export_group_info](./cloud/export_group_info.py)
5. [./cloud/delete_group](./cloud/delete_group.py)
6. [./cloud/create_group](./cloud/create_group.py)  

This API in not available in <span style="color:red">Azure DevOps Server v2019.Update1.1</span> so [TFSSecurity](https://docs.microsoft.com/en-us/azure/devops/server/command-line/tfssecurity-cmd?view=azure-devops-2019&viewFallbackFrom=azure-devops) CLI must be used  
TFSSecurity CLI can be executed on server where Azure DevOps is installed, so you have to install agent on that server (obviously Windows-based) machine  
This is annoying because Python tasks on self-managed Windows agents are problematic, so I had to install Python manually and wrapped Python calls into PowerShell in tasks  
Another important thing is account used to run Azure DevOps agent - it must have admin permissions to use TFSSecurity and by default it's just a network service. So carefully control who can use that agent  
The last but not least complain about TFSSecurity is it's output - [poorly formatted console output](https://prnt.sc/ruxi6y ). No YAML. No CSV. No JSON. So I had to develop a few workarounds to manage it, e.g. [./onprem/export_group_info.py](./onprem/export_group_info.py)  
Hope separate boiler in hell is waiting for TFSSecurity CLI developers :pray:  

`https://feeds.dev.azure.com` version `5.0-preview.1` (can be switched to `5.1-preview.1` if necessary):
1. [./common/export_feed_info](./common/export_feed_info.py)
2. [./common/get_feed_acl](./common/check_feed_permissions.py)
3. [./common/create_feed](./common/create_feed.py)
4. [./common/set_feed_acl](./common/set_feed_permissions.py)  

This API in not available in <span style="color:red">Azure DevOps Server v2019.Update1.1</span> so [regular one](https://docs.microsoft.com/en-us/rest/api/azure/devops/artifacts/feed%20%20management/create%20feed?view=azure-devops-server-rest-5.0) must be used  
It has an important limitation - feeds can not be created in project scope, only on collection level  

`https://vsrm.dev.azure.com` version `5.0` (can be switched to `5.1` if necessary):
1. [./common/create_tmp_release_pipeline](./common/create_tmp_release_pipeline.py)
2. [./common/delete_tmp_release_pipeline](./common/delete_tmp_release_pipeline.py)

For on-premise link will be `server_url/collection`, e.g. `https://ados.demo.kagarlickij.com/DefaultCollection`  

## Personal vs System access token
Default permissions of System access token are not enough to perform all CRUD actions  
Those permissions can be extended, but it's too dangerous because other pipelines will use this token too  
So solution is to create another "root" user and use it's Personal Access Token  

## Azure DevOps API throttling
I never had `429` from Azure DevOps API but I had number of situations when after received `200` code change wasn't present  
So I added `time.sleep(1)` to [./common/set_permissions](./common/set_permissions.py) script and a few pipeline tasks with `sleep 10` to wait until certain resources are created  

## Response codes
Python `requests.exceptions.RequestException` is happy with all `2**` codes but some Azure DevOps APIs respond with multiple `2**` codes for multiple results  
So I had to add `status_code` of the response to match desired e.g. `204` in [./cloud/delete_group](./cloud/delete_group.py) which is bit different from [documentation](https://docs.microsoft.com/en-us/rest/api/azure/devops/graph/groups/delete?view=azure-devops-rest-5.0)  

## Organization
All scripts have `--organization` parameter to enter API address, e.g. `https://dev.azure.com/kagarlickij` for cloud or `https://ados.demo.kagarlickij.com/DefaultCollection` for on-premise
Exception is [./cloud/export_project_info](./cloud/export_project_info.py) which has `https://dev.azure.com` and `https://vssps.dev.azure.com` hardcoded so you insert bare organization name instead of full link  

## Project scope descriptor vs Project ID
Both `projectId` and `projectScopeDescriptor` are exported as environment variables for future usage by [./cloud/export_project_info.py](./cloud/export_project_info.py) script  
`projectId` value is necessary to obtain `projectScopeDescriptor` value  

`https://vssps.dev.azure.com` API uses [projectScopeDescriptor](https://docs.microsoft.com/en-us/rest/api/azure/devops/graph/descriptors/get?view=azure-devops-rest-5.1) to identify project to work with  

`https://dev.azure.com` API uses tokens - entity that consist of [projectId](https://docs.microsoft.com/en-us/rest/api/azure/devops/core/projects/get%20project%20properties?view=azure-devops-rest-5.1#uri-parameters) and some separator characters  

## Tokens
Tokens worse some additional explanations: as per [documentation](https://docs.microsoft.com/en-us/azure/devops/cli/security_tokens?view=azure-devops) Tokens are arbitrary strings representing resources in Azure DevOps  
Token format differs per resource type, however hierarchy and separator characters are common between all tokens  
To get Token for security namespace run `GET https://dev.azure.com/{organization}/_apis/accesscontrollists/{securityNamespaceId}?api-version=5.1` (security namespaces are described down below)  

For Project namespace token format is `$PROJECT:vstfs:///Classification/TeamProject/{projectId}`  
For Git Repositories namespace token format is `repoV2/{projectId}`  
For AnalyticsViews namespace token format is `$/Shared/{projectId}`  
For Library namespace token format is `Library/{projectId}`  
For Build and ReleaseManagement it's just `{projectId}`  

Those are used in [./common/get_permissions](./common/check_permissions.py) and [./common/set_permissions](./common/set_permissions.py) conditions  

## Security namespaces
As per [documentation](https://docs.microsoft.com/en-us/rest/api/azure/devops/security/security%20namespaces?view=azure-devops-rest-5.1) security namespaces are used to store access control lists (ACLs) of tokens  
You can get list of namespaces with `GET 'https://dev.azure.com/{organization}/_apis/securitynamespaces?api-version=5.1'`  
As for now, there're 60 namespaces, for our purposes we'll use a few of them:
`52d39943-cb85-4d7f-8fa8-c6baac873819` for Project  
`d34d3680-dfe5-4cc6-a949-7d9c68f73cba` for AnalyticsViews  
`2e9eb7ed-3c0a-47d4-87c1-0ffdd275fd87` for Git Repositories  
`b7e84409-6553-448a-bbb2-af228e07cbeb` for Library  
`33344d9c-fc72-4d6f-aba5-fa317101a7e9` for Builds  
`c788c23e-1b46-4162-8f5e-d7585343b5de` for ReleaseManagement  

# Azure DevOps Security basics
## Numbers for permissions
Permissions for majority of resources are present as sum of "bits" (numbers) for actions in namespace  
e.g. in AnalyticsViews "Read" is `1` and "Execute" is `8` so "allow" field in ACL's "acesDictionary" must be `9`  
The same logic is fair for "deny" rules, and resulting ACL looks like [this](https://prnt.sc/rqat79)  
Exception is Artifact feed permissions model, there are no "acesDictionary" and "bits", more simple concept of "roles" is used instead: [screenshot](https://prnt.sc/rqaz0p)

## Create entity vs set permissions
As mentioned above permissions are set in resource's ACL and existing entities (user or group) must be used  
So there's no way to create user/group and set permissions at the same time  
To provide cross-account capabilities in ACLs [descriptors](https://docs.microsoft.com/en-us/rest/api/azure/devops/graph/?view=azure-devops-rest-5.1#descriptors) are used instead of user/group bare names  

# Azure DevOps Artifact feeds
## Artifact feed name is still "busy" after feed is deleted
Current solution creates dedicated feed for each project (but project-scoped only in the cloud)  
It might be a situation when project has to be deleted and then created again  
But feed with the same name will fail to create even if it was deleted from "Deleted feeds" (trashbox for feeds)  
e.g. when I'm trying to create `test1` feed I'm getting response ["A feed named 'test1' already exists."](https://prnt.sc/rqp4qy) but when I'm listing feeds `test1` does not exist in both [API](https://prnt.sc/rqp5na) and [UI](https://prnt.sc/rqp6fo) including ["Deleted feeds"](https://prnt.sc/rqp62s)  

# `create-project` pipeline
`create-project` pipeline creates new project based on "security template" and consist of the following steps:
1. Create project  
`--processTemplate` param set to be Scrum ('6b724908-ef14-45cf-84f8-768b5384da45') by default  
Process templates ids can be listed with [Processes - List API](https://docs.microsoft.com/en-us/rest/api/azure/devops/processes/processes/list?view=azure-devops-rest-5.1)  
`--projectDescription` param is optional and empty by default  
`sourceControlType` is hardcoded to be Git  
`visibility` is hardcoded to be Private  

2. Export project-related info  
As mentioned above `PROJECT_ID` and `PROJECT_SCOPE_DESCRIPTOR` vars are exported for further usage  

3. Create tmp Release pipeline  
Unlike builds, you have to have at least one Release pipeline to be able set permissions in ReleaseManagement namespace  
Built-in 'Release Administrators' group is also created automatically by Azure DevOps after first release pipeline is created  
So we have to create dummy release pipeline and delete it later  

4. Delete built-in groups  
Since we will use our custom groups default (built-in) groups can be deleted  
However 'Project Valid Users', 'Project Administrators' and '$projectName Team' groups can not be deleted  
I prefer to delete default groups because '$projectName Team' inherits some undesired permissions from other default groups  
If people are added to default 'Project Administrators' group `check-project` pipeline will alert since it is not desired  

5. Create custom groups  
`Administrators` - ADOS setup, Releases setup (until we have it as code), security changes (both ADOS and app related)  
`Developers` - develop apps, develop build pipelines, watching Builds and Releases  
`Product Owners` - manage Release activities  
`Auditors` - checking security configs (current vs desired)  
Each group has prefix with project name (e.g. `prj01-developers`) to make cross-project access easy if it's required  

6. Export group-related info  
Exports group SID as a variable for further usage  
Format of SID from time to time causes incorrect padding in Python so [fix](https://stackoverflow.com/questions/2941995/python-ignore-incorrect-padding-error-when-base64-decoding) is applied  

7. Set Project permissions for each group  
Here's the first time when [./common/set_permissions.py](./common/set_permissions.py) script comes into the game  
It will be used to set almost all permissions so threat it with extra care  

8. Set Analytics permissions for each group  
Analytics views are located in the same UI section Project permissions but have different security namespace and token format  

9. Set Library permissions for each group  
Variable groups permissions are crucial piece, so pay extra attention to this permissions  

10. Set Git repos settings [task](./common/set_git_policy.py) creates cross-repo policy that requires at least 1 reviewer before merge into `master` branch  

11. Set Git permissions for each group  
This security namespace also has different token format and [./common/set_permissions.py](./common/set_permissions.py) knows about that  

12. Set Build permissions for each group  
Nothing too special here, token in this security namespace is equal to project id  

13. Set Release permissions for each group  
This task will fail if tmp Release pipeline was not created (Step #3)  

14. Delete tmp Release pipeline  
Dummy release pipeline has not be present anymore

15. Create Artifact feed (optional)  
For cloud scenario `createArtifactFeed` parameter must be set `true` for feed to be created  
For on-premise [parameters are not supported](https://stackoverflow.com/questions/62449727/azure-devops-server-2019-condition-for-task-execution) so `createArtifactFeed` is variable used in [create-feed](./onprem/templates/create-feed.yml) and [check-feed-permissions](./onprem/templates/check-feed-permissions.yml) for the same purpose  
`https://feeds.dev.azure.com/{organization}/_apis/packaging/feeds?api-version=5.0-preview.1` API used for cloud and `{server_ur}/{collection}/_apis/packaging/feeds?api-version=5.0-preview.1` API used for on-premise  
Feed has default capabilities and upstream disabled - all is hardcoded in [./common/create_feed.py](./common/create_feed.py)  

16. Export feed info  
`FEED_ID` variable is exported for further usage  

17. Set feed permissions
As described above, feeds use roles instead of permissions "bits" so [./common/set_feed_permissions.py](./common/set_feed_permissions.py) script is used instead of [./common/set_permissions.py](./common/set_permissions.py)  

# `check-project` pipeline
1. Export project-related info  
As mentioned above `PROJECT_ID` and `PROJECT_SCOPE_DESCRIPTOR` variables are exported for further usage  

2. Export group-related info  
Exports group SID as a var for further usage  
Format of SID from time to time causes incorrect padding in Python so [fix](https://stackoverflow.com/questions/2941995/python-ignore-incorrect-padding-error-when-base64-decoding) is applied  

3. Check list of groups  
Checks if no additional groups were created and/or existing groups deleted/renamed  

4. Check group members  
Checks only default groups that can't be deleted: 'Project Valid Users' and 'Project Administrators'  
Nobody should be added to those groups, so desired quantity of members is 0  
However creator of the project (user, whose PAT was used in pipeline) is set to be member of 'Project Administrators', so for 'Project Administrators' desired quantity of members is 1  

5. Check Project permissions for each group  
[./common/check_permissions.py](./common/check_permissions.py) script will check if current Project scope permissions match desired  
As well as [./common/set_permissions.py](./common/set_permissions.py) it knows about different tokens for different security namespaces  

6. Check Analytics permissions for each group  
[./common/check_permissions.py](./common/check_permissions.py) script will check if current Analytics scope permissions match desired  

7. Check Library permissions for each group  
[./common/check_permissions.py](./common/check_permissions.py) script will check if current Library scope permissions match desired  

8. Check Git repos settings [task](./common/check_git_policy.py) performs the following checks on all repos in the project:  
Check if all branches follow naming standards: allowed names are `master`, `feature/` and `bugfix/`  
Check if all branches are up to date: latest commit shouldn't be older than X days (see `ados-git-params-$projectName` variable group below for details), however `master` branch is excluded from this check  
Check if all Pull requests are up to date: pull requests shouldn't be older than X days (see `ados-git-params-$projectName` variable group below for details)  
All 3 checks generate warnings, not errors  
The latest one checks if `master` branch has at least 1 reviewer in the corresponding policy, and if not error will be raised  
Some repos can be excluded from checking by putting repo name to [excluded_repos.txt](excluded_repos.txt) file  

9. Check Git permissions for each group  
[./common/check_permissions.py](./common/check_permissions.py) script will check if current Git scope permissions match desired  

10. Check Build permissions for each group  
[./common/check_permissions.py](./common/check_permissions.py) script will check if current permissions match desired  

11. Check Release permissions for each group  
[./common/check_permissions.py](./common/check_permissions.py) script will check if current permissions match desired  

12. Export feed info (optional)  
`FEED_ID` var is exported for further usage  
Conditions are the same as for `create-project`

13. Check Artifact feed permissions for each group (optional)  
[./common/check_feed_permissions.py](./common/check_feed_permissions.py) script is used instead of [./common/check_permissions.py](./common/check_permissions.py) because `https://feeds.dev.azure.com` API is used  
Conditions are the same as for `create-project`  

# Pipelines execution
## Triggers
`create-project` pipeline is executed only once, so no triggers needed  
`check-project` pipeline must be executed on schedule, default is daily at 2AM  
Execution time is about 1 minute, so schedule can be set to be hourly  
However there's still a risk that person will be added to 'Project Administrators' group, perform some "bad" actions, removed from the group and `check-project` pipeline will not catch it because those actions are less than 1h long  
This is an advanced scenario and to address it real-time log analytics must be set to watch Azure DevOps logs  

## Variables
Both `create-project` and `check-project` pipelines must used the same variables in variable groups  
Moreover, it's recommended not to change variables after `create-project` execution otherwise "current desired state" will not match "initial desired state"  
Azure DevOps variable groups don't have history of changes and versioning so it's recommended to use [linking with Azure Key Vault](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups?view=azure-devops&tabs=yaml#link-secrets-from-an-azure-key-vault)  

`projectName` is the only variable hardcoded in pipelines, change it's value right after forking this repo  

`ados-group-names-$projectName` variable group contains names of custom groups to create and names of SIDs to use as environment variable names, example:  
| Name | Value |
| ------------- | ------------- |
| administrators-group-sid | $(administrators-group-name)-sid |
| administrators-group-name | $(projectName)-administrators |
| auditors-group-sid | $(auditors-group-name)-sid |
| auditors-group-name | $(projectName)-auditors |
| developers-group-sid | $(developers-group-name)-sid |
| developers-group-name | $(projectName)-developers |
| product-owners-group-sid | $(product-owners-group-name)-sid |
| product-owners-group-name | $(projectName)-product-owners |

If you want to add more groups or remove some of existing don't forget to change both variable group and pipeline's tasks

`ados-acls-$projectName` group contains "security bits" for each group per each security namespace, example:
| Name | Value |
| ------------- | ------------- |
| administrators-analytics-allow-permissions | 6 |
| administrators-analytics-deny-permissions | 0 |
| administrators-build-allow-permissions | 65535 |
| administrators-build-deny-permissions | 0 |
| administrators-feed-permissions | administrator |
| administrators-git-allow-permissions | 65534 |
| administrators-git-deny-permissions | 0 |
| administrators-library-allow-permissions | 19 |
| administrators-library-deny-permissions | 0 |
| administrators-project-allow-permissions | 11729915 |
| administrators-project-deny-permissions | 4259844 |
| administrators-release-allow-permissions | 65535 |
| administrators-release-deny-permissions | 0 |
| auditors-analytics-allow-permissions | 0 |
| auditors-analytics-deny-permissions | 6 |
| auditors-build-allow-permissions | 1025 |
| auditors-build-deny-permissions | 31742 |
| auditors-feed-permissions | reader |
| auditors-git-allow-permissions | 2 |
| auditors-git-deny-permissions | 65532 |
| auditors-library-allow-permissions | 1 |
| auditors-library-deny-permissions | 0 |
| auditors-project-allow-permissions | 2097665 |
| auditors-project-deny-permissions | 13892094 |
| auditors-release-allow-permissions | 33 |
| auditors-release-deny-permissions | 4062 |
| developers-analytics-allow-permissions | 0 |
| developers-analytics-deny-permissions | 6 |
| developers-build-allow-permissions | 1921 |
| developers-build-deny-permissions | 30846 |
| developers-feed-permissions | collaborator |
| developers-git-allow-permissions | 16758 |
| developers-git-deny-permissions | 48776 |
| developers-library-allow-permissions | 17 |
| developers-library-deny-permissions | 0 |
| developers-project-allow-permissions | 2104105 |
| developers-project-deny-permissions | 13885638 |
| developers-release-allow-permissions | 97 |
| developers-release-deny-permissions | 3998 |
| product-owners-analytics-allow-permissions | 6 |
| product-owners-analytics-deny-permissions | 0 |
| product-owners-build-allow-permissions | 1025 |
| product-owners-build-deny-permissions | 31742 |
| product-owners-feed-permissions | reader |
| product-owners-git-allow-permissions | 16486 |
| product-owners-git-deny-permissions | 49048 |
| product-owners-library-allow-permissions | 1 |
| product-owners-library-deny-permissions | 0 |
| product-owners-project-allow-permissions | 11723265 |
| product-owners-project-deny-permissions | 4266494 |
| product-owners-release-allow-permissions | 2169 |
| product-owners-release-deny-permissions | 1926 |

`ados-git-params-$projectName` group contains parameters for git checks, example:
| Name | Value |
| ------------- | ------------- |
| maxCommitAge | 15 |
| maxPullRequestAge | 5 |
| minApproverCount | 1 |

`ados-secrets` group contains Azure DevOps Personal Access Token that is used for all API actions, described in details above in "Personal vs System access token" section
| Name | Value |
| ------------- | ------------- |
| cloud_pat | ***** |
| onprem_pat | ***** |
`*****` - because marked as secret  
If you use cloud Azure DevOps you need only `cloud_pat` and if you use on-premise Azure DevOps you need only `onprem_pat`  

`github-secrets` group contains GitHub Personal Access Token that is used for all API actions, described in details in "Build" section
| Name | Value |
| ------------- | ------------- |
| gitHubPat | ***** |
`*****` - because marked as secret  

## Azure DevOps specific syntax in scripts
1. All `print` functions have `[INFO]` or `[ERROR]` prefixes to make output more readable and properly [colored in Azure DevOps logs](https://developercommunity.visualstudio.com/content/problem/440605/write-host-foreground-color-with-powershell-task-i.html), [example](https://prnt.sc/rqzu2x)  
However <span style="color:red">Azure DevOps Server v2019.Update1.1</span> supports only `error` and `warning` and doesn't support `section`, `command`, `debug`, etc.  
2. Environment variables are set via [`task.setvariable` logging command](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/variables?view=azure-devops&tabs=yaml%2Cbatch#set-variables-in-scripts)  

# Contribution
## pre-commit and pre-push hooks
To keep code clean the following measures are set:  
1. Pre-commit hook: before each commit code is formatted with [Black](https://github.com/psf/black) in [pre-commit-config](.pre-commit-config.yaml) config  
2. Pre-push hook: before each commit code is validated with [Bandit](https://github.com/PyCQA/bandit) in [pre-commit-config](.pre-commit-config.yaml) config  

To install those checks on your machine:  
1. Install [pre-commit](https://pre-commit.com/#intro) tool: `pip install pre-commit`  
2. Install pre-commit for the repo: `pre-commit install && pre-commit install -t pre-push`  

If you need to remove pre-commit run: `pre-commit install && pre-commit uninstall -t pre-push`  

Both checks are executed only if Python code was updated  
Both checks require binaries to be installed in advance: `pip install black` and `pip install bandit`  

## Pull request validation:
1. `Lint Python code`: Both [Black](https://github.com/psf/black) and [Bandit](https://github.com/PyCQA/bandit) checks are up to developer, but before code is merged into `master` it must pass `pylint` check and Pull request will be marked as failed if score is lower than 8/10  
A few irrelevant for the project issues are added as exceptions to [pylintrc](.pylintrc)  
2. `Create project` to verify if code in Pull request works - all steps match `create-project` pipeline, artifact feed is enabled  
Project name is based on Pull request number: `prj-template-$(Build.BuildId)-prv`  
3. `Run positive project check` to verify if it was created correctly and matches desired security rules - all steps match `check-project` pipeline, artifact feed is enabled  
4. `Break project`: Change security settings to make project "broken"  
5. `Run negative project check` to verify if security violations are noticed by checks - all steps match `check-project` pipeline, artifact feed is enabled  
This job's successful result is "warning", "success" will mean fail like in typical negative check  
6. `Delete project` when checks are done tmp project is deleted  

## Build
When code is merged into `master` branch build job generates pylint badge referenced on top of this file  
[generate_pylint_badge](./common/generate_pylint_badge.py) script uses [pylint](https://www.pylint.org/) to generate score, [anybadge](https://pypi.org/project/anybadge/) to generate png and [GitHub Gist API](https://developer.github.com/v3/gists/) to push svg to [GitHub Gist](https://gist.githubusercontent.com/kagarlickij/780fabe68201e08c8f2151ad02898bad/raw/pylint.svg) which is used for svg hosting  
[Build pipeline](./cloud/build.yml) installs `pylint` and `anybadge` binaries on Azure DevOps agent for [generate_pylint_badge](./common/generate_pylint_badge.py) script because Python packages for both `pylint` and `anybadge` don't work correctly: [anybadge issue](https://github.com/jongracecox/anybadge/issues/42), [epylint issue](https://stackoverflow.com/questions/61485537/epylint-output-to-variable)

# Known issues
1. `pylint` cmd in [generate_pylint_badge](./common/generate_pylint_badge.py) causes Bandit `[B602:subprocess_popen_with_shell_equals_true]` issue  
It's better to replace `pylint` cmd with `epylint` but it has an issue with [output to variable](https://stackoverflow.com/questions/61485537/epylint-output-to-variable)  
2. For on-premise `pylint` execution for all files [doesn't work on windows](https://stackoverflow.com/questions/62488844/run-pylint-against-all-files-in-windows)  