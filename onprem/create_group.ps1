Param(
    [Parameter(Mandatory=$True)]
    [String]
    $ORGANIZATION,

    [Parameter(Mandatory=$True)]
    [String]
    $PROJECT_ID,

    [Parameter(Mandatory=$True)]
    [String]
    $GROUP_NAME,

    [Parameter(Mandatory=$True)]
    [String]
    $GROUP_DESCRIPTION
)

Set-Location -Path 'C:\Program Files\Azure DevOps Server 2019\Tools'
.\TFSSecurity.exe /gc vstfs:///Classification/TeamProject/$PROJECT_ID $GROUP_NAME $GROUP_DESCRIPTION /collection:$ORGANIZATION
