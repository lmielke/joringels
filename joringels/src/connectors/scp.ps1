# WIN shell script to be run locally in PS
# remote RMUSER and pwd to copy ssh files to remote location
Write-Host "`nscp.ps1" -BackgroundColor yellow -ForegroundColor black


$hostIp = $args[0]
$locPath = $args[1]
$rmPath = $args[2]
$username = $args[3]
$password = $args[4]

if ($args.Length -lt 3){
    Write-Host "`nMissing parameter" -ForegroundColor red
    Write-Host "`tusername:$($args[0]), hostIp:$($args[1]), locPath:$($args[2]), rmPath:$($args[3])"
    Write-Host "Example: my_scp 998-testing ~/python_venvs"
    exit 0
}

Write-Host "`tNow uploading to $username@$hostIp, files: $locPath -> $rmPath" -ForegroundColor yellow
if (($username -eq $null) -or ($password -eq $null)){
    Write-Host "`t`tEnter target credentials! Use pwd-user autotype:" -ForegroundColor magenta
    $username = Read-Host -Prompt "`t`t`tusername $username@$hostIp"
    $password = Read-Host -Prompt "`t`t`tpwd $username@$hostIp"
}

$password = ConvertTo-SecureString -String $password -AsPlainText -Force

Write-Host "Creds: $username, key: $password" -ForegroundColor green
$credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $username, $password
Set-SCPItem  -Credential $credential -ComputerName $hostIp -Path $locPath -Destination $rmPath -Force
Write-Host "`tUpload successful" -ForegroundColor green