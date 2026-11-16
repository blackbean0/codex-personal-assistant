[CmdletBinding(SupportsShouldProcess = $true)]
param()
$ErrorActionPreference = 'Stop'
foreach ($AssistantTask in 'PersonalAssistant-Engine', 'PersonalAssistant-Sync') {
    if ((Get-ScheduledTask -TaskName $AssistantTask -ErrorAction SilentlyContinue) -and
        $PSCmdlet.ShouldProcess($AssistantTask, 'Unregister scheduled task')) {
        Unregister-ScheduledTask -TaskName $AssistantTask -Confirm:$false
    }
}
# Personal data and running engine processes are deliberately preserved.
Write-Output 'Scheduled task removal completed. No personal files were removed.'
