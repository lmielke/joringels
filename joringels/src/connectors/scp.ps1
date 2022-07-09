# WIN shell script to be run locally in PS
# remote RMUSER and pwd to copy ssh files to remote location
Write-Host "`nscp.ps1" -BackgroundColor yellow -ForegroundColor black


$rmUserName = $args[0]
$rmHost = $args[1]
$localPath = $args[2]
$rmPath = $args[3]
$rmKey = ConvertTo-SecureString -String $args[4] -AsPlainText -Force


Write-Host "`tNow uploading to $rmHost, files: $localPath -> $rmPath" -ForegroundColor yellow
Write-Host "`r`nCreds: $rmUserName, key: $rmKey" -ForegroundColor green
$Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $rmUserName, $rmKey
Set-SCPItem  -Credential $credential -ComputerName $rmHost -Path $localPath -Destination $rmPath
Write-Host "`tUpload successful" -ForegroundColor green