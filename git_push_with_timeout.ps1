param(
    [int]$TimeoutSeconds = 20
)

$ErrorActionPreference = "Stop"
$repoPath = "c:\Users\SmithGz\CodeBuddy\20260512224659\single-choice-practice"
Set-Location $repoPath

# Supress git prompts
$env:GIT_TERMINAL_PROMPT = 0
$env:GCM_INTERACTIVE = "never"

function Run-WithTimeout {
    param([string]$Command, [string]$Label)
    Write-Host "▶ $Label..." -ForegroundColor Cyan
    $job = Start-Job -ScriptBlock {
        param($c, $p)
        Set-Location $p
        Invoke-Expression $c
    } -ArgumentList @($Command, $repoPath)

    $result = $null
    $completed = $job | Wait-Job -Timeout $TimeoutSeconds
    if ($completed -eq $null) {
        $job | Stop-Job -PassThru | Remove-Job -Force
        Write-Host "✖ TIMEOUT ($TimeoutSeconds s): $Label" -ForegroundColor Red
        return $false, ""
    } else {
        $result = $job | Receive-Job
        $job | Remove-Job -Force
        Write-Host "✓ Done: $Label" -ForegroundColor Green
        return $true, $result
    }
}

# Step 1: git add
$ok, $out = Run-WithTimeout "git add -A" "git add"
if (-not $ok) { exit 1 }

# Step 2: git status (check for changes)
$ok, $out = Run-WithTimeout "git status --short" "git status"
if (-not $ok) { exit 1 }
Write-Host $out

# Step 3: Check if there are changes to commit
if ([string]::IsNullOrWhiteSpace($out)) {
    Write-Host "没有变更需要提交，跳过 commit 和 push" -ForegroundColor Yellow
    exit 0
}

# Step 4: git commit
$ok, $out = Run-WithTimeout "git commit -m 'feat: 导入10000道计算机基础题库 + 更新文档'" "git commit"
if (-not $ok) { exit 1 }
Write-Host $out

# Step 5: git pull (rebase to avoid conflicts)
$ok, $out = Run-WithTimeout "git pull --rebase --autostash" "git pull --rebase"
if (-not $ok) { 
    Write-Host "⚠ git pull 失败或超时，尝试直接 push..." -ForegroundColor Yellow
} else {
    Write-Host $out
}

# Step 6: git push
$ok, $out = Run-WithTimeout "git push" "git push"
if (-not $ok) {
    Write-Host "⚠ git push 超时，可能是网络问题。提交已在本地完成" -ForegroundColor Yellow
    exit 1
}
Write-Host $out

Write-Host "`n✅ 全部完成！" -ForegroundColor Green
