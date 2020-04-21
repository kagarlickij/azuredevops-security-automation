Param(
    [Parameter(Mandatory=$True)]
    [String]
    $ORGANIZATION,

    [Parameter(Mandatory=$True)]
    [String]
    $PROJECT_NAME,

    [Parameter(Mandatory=$True)]
    [String]
    $GROUP_NAME
)

Set-Location -Path 'C:\Program Files\Azure DevOps Server 2019\Tools'
.\TFSSecurity.exe /gd "[$PROJECT_NAME]\$GROUP_NAME" /collection:$ORGANIZATION
