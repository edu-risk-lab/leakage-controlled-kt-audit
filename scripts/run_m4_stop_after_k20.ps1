# Wait for k=20 Phase B to finish, stop the multi-cell sweep, then run open corner if missing.
$ErrorActionPreference = "Continue"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Log = Join-Path $Root "logs\m4\watchdog_stop_after_k20.log"
$Py = Join-Path $Root ".venv\Scripts\python.exe"
$K20Csv = Join-Path $Root "results\q1\m4_q0.5_k20_Kinf_tau0.1\baseline_fold_results.csv"
$OpenCsv = Join-Path $Root "results\q1\m4_q0.5_k5_Kinf_tau0.1\baseline_fold_results.csv"

function Write-Log([string]$Msg) {
    $line = "{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Msg
    Add-Content -Path $Log -Value $line
    Write-Host $line
}

New-Item -ItemType Directory -Force -Path (Split-Path $Log) | Out-Null
Write-Log "Watchdog started: stop 7-cell queue after k=20; open corner if needed."

while (-not (Test-Path $K20Csv)) {
    Start-Sleep -Seconds 120
    if (((Get-Date) - (Get-Item $Log).LastWriteTime).TotalHours -gt 0.5) {
        Write-Log "Still waiting for k=20 CSV..."
    }
}

Write-Log "k=20 done: $K20Csv"

# Stop multi-cell sweep (do not touch a lone open-corner job).
Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue | ForEach-Object {
    $cmd = $_.CommandLine
    if ($null -eq $cmd) { return }
    if ($cmd -like "*run_m4_qk_sweep*" -and $cmd -like "*q0.5_kinf_Kinf*") {
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        Write-Log "Stopped 7-cell sweep PID $($_.ProcessId)"
    }
    if ($cmd -like "*baseline_runner*" -and $cmd -like "*q0.5_kinf_Kinf*") {
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        Write-Log "Stopped stray kinf runner PID $($_.ProcessId)"
    }
}

Start-Sleep -Seconds 5

if (Test-Path $OpenCsv) {
    Write-Log "Open corner already done: $OpenCsv - nothing to run."
    exit 0
}

Write-Log "Starting open corner q0.5_k5_Kinf_tau0.1 fold 0..."
$openLog = Join-Path $Root "logs\m4\phase_b_open_corner_fold0.log.err"
$env:PYTHONUNBUFFERED = "1"
& $Py (Join-Path $Root "scripts\run_m4_qk_sweep.py") `
    --phase b `
    --cells q0.5_k5_Kinf_tau0.1 `
    --fold-idx 0 `
    --log-level INFO `
    2>&1 | Tee-Object -FilePath $openLog
Write-Log ("Open corner finished exit=" + $LASTEXITCODE)
