$ErrorActionPreference = "Stop"

$ApiUrl = $env:API_URL
if (-not $ApiUrl) {
  $ApiUrl = "http://127.0.0.1:8000"
}

Write-Host "Testing BeingAI API at $ApiUrl"

$health = Invoke-RestMethod "$ApiUrl/api/health"
if ($health.status -ne "ok") {
  throw "Health check failed"
}
Write-Host "OK health"

$ready = Invoke-RestMethod "$ApiUrl/api/ready"
if ($ready.status -notin @("ready", "degraded")) {
  throw "Readiness check returned unexpected status: $($ready.status)"
}
Write-Host "OK ready ($($ready.status))"

$integrations = Invoke-RestMethod "$ApiUrl/api/integrations"
if ($integrations.Count -lt 5) {
  throw "Expected at least 5 integrations"
}
Write-Host "OK integrations"

$body = @{
  prompt = "When someone fills my form, send WhatsApp message and save lead."
  business_type = "local_shop"
} | ConvertTo-Json

$automation = Invoke-RestMethod `
  -Uri "$ApiUrl/api/automations/create" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body

if (-not $automation.id -or -not $automation.trigger -or $automation.actions.Count -lt 1) {
  throw "Automation creation returned an invalid payload"
}
Write-Host "OK automation created: $($automation.title)"
Write-Host "Trigger: $($automation.trigger)"
Write-Host "Actions: $($automation.actions -join ', ')"

$retry = Invoke-RestMethod `
  -Uri "$ApiUrl/api/automations/$($automation.id)/retry" `
  -Method Post

if ($retry.status -notin @("success", "failed", "queued")) {
  throw "Retry endpoint returned an unexpected status: $($retry.status)"
}
Write-Host "OK retry executed: $($retry.status)"
if ($retry.run_count -lt 1) {
  throw "Expected run_count to increase after retry"
}
Write-Host "OK run_count=$($retry.run_count)"

Write-Host "Local smoke test passed"

