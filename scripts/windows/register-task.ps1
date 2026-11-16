# Windows native scheduled tasks. Validate first; registration is opt-in.
[CmdletBinding(SupportsShouldProcess = $true)]
param([switch]$ValidateOnly)

$ErrorActionPreference = 'Stop'
$AssistantRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
if ($AssistantRoot.StartsWith('\\')) { throw 'Use a local Windows checkout for scheduled tasks.' }
$AssistantPython = Join-Path $AssistantRoot '.venv\Scripts\pythonw.exe'
if (-not (Test-Path -LiteralPath $AssistantPython)) { throw 'Run bin\setup.cmd first.' }
$AssistantCliPython = Join-Path $AssistantRoot '.venv\Scripts\python.exe'
& $AssistantCliPython -X utf8 -m pa doctor
if ($LASTEXITCODE -ne 0) { throw 'Resolve diagnostic errors before registering tasks.' }
if ($ValidateOnly) { Write-Output 'Scheduled task configuration: PASS (no tasks registered)'; return }

$AssistantUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$AssistantPrincipal = New-ScheduledTaskPrincipal -UserId $AssistantUser -LogonType Interactive -RunLevel Limited
$AssistantLogon = New-ScheduledTaskTrigger -AtLogOn -User $AssistantUser
$AssistantEngine = New-ScheduledTaskAction -Execute $AssistantPython -Argument '-X utf8 -m pa watch' -WorkingDirectory $AssistantRoot
$AssistantSync = New-ScheduledTaskAction -Execute $AssistantPython -Argument '-X utf8 -m pa run --full' -WorkingDirectory $AssistantRoot
$AssistantEngineSettings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -MultipleInstances IgnoreNew -RestartCount 5 -RestartInterval (New-TimeSpan -Minutes 1)
$AssistantSyncSettings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -MultipleInstances IgnoreNew
$AssistantSyncTriggers = @($AssistantLogon, (New-ScheduledTaskTrigger -Daily -At 7:00),
    (New-ScheduledTaskTrigger -Daily -At 13:00), (New-ScheduledTaskTrigger -Daily -At 19:00))
if ($PSCmdlet.ShouldProcess('PersonalAssistant-Engine and PersonalAssistant-Sync', 'Register Windows login and sync tasks')) {
    Register-ScheduledTask -TaskName 'PersonalAssistant-Engine' -Action $AssistantEngine -Trigger $AssistantLogon `
        -Settings $AssistantEngineSettings -Principal $AssistantPrincipal -Description 'Codex personal assistant engine' -Force | Out-Null
    Register-ScheduledTask -TaskName 'PersonalAssistant-Sync' -Action $AssistantSync -Trigger $AssistantSyncTriggers `
        -Settings $AssistantSyncSettings -Principal $AssistantPrincipal -Description 'Personal assistant synchronization' -Force | Out-Null
    Write-Output 'Registered. Start manually with Start-ScheduledTask -TaskName PersonalAssistant-Engine'
}
