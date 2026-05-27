# Build paper/main.tex (Springer LNNS / LNCS llncs class) from repo root.
param(
    [string]$JobName = "main"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

$MiktexBin = Join-Path $Root "tools\miktex\miktex\bin\x64"
if (Test-Path $MiktexBin) {
    $env:PATH = "$MiktexBin;$env:PATH"
}

function Invoke-TeX {
    param([string[]]$TeXArgs)
    Write-Host ">> pdflatex $($TeXArgs -join ' ')"
    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & pdflatex @TeXArgs 2>&1 | Write-Host
        if ($LASTEXITCODE -ne 0) { throw "pdflatex failed (exit $LASTEXITCODE)" }
    } finally {
        $ErrorActionPreference = $prevEap
    }
}

$out = "paper"
$tex = "paper/main.tex"
Invoke-TeX @("-interaction=nonstopmode", "-jobname=$JobName", "-output-directory=$out", $tex)
Push-Location $out
try {
    Write-Host ">> bibtex $JobName"
    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & bibtex $JobName 2>&1 | Write-Host
        if ($LASTEXITCODE -ne 0) { throw "bibtex failed (exit $LASTEXITCODE)" }
    } finally {
        $ErrorActionPreference = $prevEap
    }
} finally {
    Pop-Location
}
Invoke-TeX @("-interaction=nonstopmode", "-jobname=$JobName", "-output-directory=$out", $tex)
Invoke-TeX @("-interaction=nonstopmode", "-jobname=$JobName", "-output-directory=$out", $tex)

$pdf = Join-Path $out "$JobName.pdf"
Write-Host "[OK] $pdf"
