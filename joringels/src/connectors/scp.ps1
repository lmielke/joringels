# WIN shell script to be run locally in PS
# remote RMUSER and pwd to copy ssh files to remote location
Write-Host "`nscp.ps1" -BackgroundColor yellow -ForegroundColor black


Write-Host "`tNow uploading to $($args[1]): $($args[2]) -> $($args[3])" -ForegroundColor yellow
$rmUserName = $args[0]
$rmHost = $args[1]
$localPath = $args[2]
$rmPath = $args[3]
$rmKey = ConvertTo-SecureString -String $args[4] -AsPlainText -Force


$Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $rmUserName, $rmKey
Set-SCPItem  -Credential $credential -ComputerName $rmHost -Path $localPath -Destination $rmPath
Write-Host "`tUpload successful" -ForegroundColor green