# WIN shell script to be run locally in PS
# remote RMUSER and pwd to copy ssh files to remote location
Write-Host "`nscp.ps1" -BackgroundColor yellow -ForegroundColor black


$username = $args[0]
$hostIp = $args[1]
$locPath = $args[2]
$rmPath = $args[3]
$rmKey = $args[4]

if ($args.Length -lt 4){
    Write-Host "`nMissing parameter" -ForegroundColor red
    Write-Host "`tusername:$($args[0]), hostIp:$($args[1]), locPath:$($args[2]), rmPath:$($args[3])"
    Write-Host "Example: my_scp 998-testing ~/python_venvs"
    exit 0
}

Write-Host "`tNow uploading to $username@$hostIp, files: $locPath -> $rmPath" -ForegroundColor yellow
if ($rmKey -eq $null){
    $rmKey = Read-Host -Prompt "pwd $username@$hostIp"
}

$rmKey = ConvertTo-SecureString -String $rmKey -AsPlainText -Force

Write-Host "`r`nCreds: $username, key: $rmKey" -ForegroundColor green
$credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $username, $rmKey
Set-SCPItem  -Credential $credential -ComputerName $hostIp -Path $locPath -Destination $rmPath
Write-Host "`tUpload successful" -ForegroundColor green