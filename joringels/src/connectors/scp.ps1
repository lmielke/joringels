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

if (($username -eq $null) -or ($password -eq $null)){
    Write-Host "`nTarget credentials! " -nonewline
    Write-Host "AUTOTYPE hostName-pwd-user :" -ForegroundColor yellow
    $username, $hostIp = $(Read-Host -Prompt " ").split('@')
    $username = $username.Substring(4, $username.Length-4)
    $password = Read-Host -Prompt " "

}
$password = ConvertTo-SecureString -String "$password" -AsPlainText -Force
$credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $username, $password

Write-Host "`nUPLOADING ... "
Write-Host "Credential: username: " -nonewline
Write-Host "$username " -ForegroundColor yellow -nonewline
Write-Host ", key: " -nonewline
Write-Host "$password " -ForegroundColor yellow -nonewline
Write-Host "-> " -nonewline
Write-Host "$credential" -ForegroundColor yellow

Write-Host "Set-SCPItem -ComputerName" -NoNewline -ForegroundColor white
Write-Host " $hostIp" -NoNewline -ForegroundColor yellow
Write-Host " -Path" -NoNewline -ForegroundColor white
Write-Host " $locPath" -NoNewline -ForegroundColor yellow
Write-Host " -Destination" -NoNewline -ForegroundColor white
Write-Host " $rmPath" -NoNewline -ForegroundColor yellow
Write-Host " -Force`n" -ForegroundColor white


Set-SCPItem  -Credential $credential -ComputerName $hostIp -Path $locPath -Destination $rmPath -Force
Write-Host "`tUpload successful" -ForegroundColor green