Param(
    [Parameter(Mandatory=$True)]
    [String]
    $ORGANIZATION,

    [Parameter(Mandatory=$True)]
    [String]
    $PROJECT_ID
)

Set-Location -Path 'C:\Program Files\Azure DevOps Server 2019\Tools'
.\TFSSecurity.exe /g vstfs:///Classification/TeamProject/$PROJECT_ID /collection:$ORGANIZATION | Out-File -FilePath $Env:BUILD_SOURCESDIRECTORY\groups_list.txt -Encoding ASCII -Force
