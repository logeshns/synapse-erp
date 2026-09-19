$roles = @(
    @{ email = "sales@demo.com";      role = "SALES" },
    @{ email = "warehouse@demo.com";  role = "WAREHOUSE" },
    @{ email = "accountant@demo.com"; role = "ACCOUNTANT" },
    @{ email = "manager@demo.com";    role = "MANAGER" },
    @{ email = "owner@demo.com";      role = "OWNER" }
)

foreach ($r in $roles) {
    $body = @{ email = $r.email; password = "Demo@12345" } | ConvertTo-Json
    $login = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method Post -ContentType "application/json" -Body $body
    $me = Invoke-RestMethod -Uri "http://localhost:8000/auth/me" -Headers @{ Authorization = "Bearer $($login.access_token)" }
    
    if ($me.role -eq $r.role) {
        Write-Host "OK   $($r.email) -> role $($me.role)" -ForegroundColor Green
    } else {
        Write-Host "FAIL $($r.email) -> expected $($r.role), got $($me.role)" -ForegroundColor Red
    }
}

# Negative case: wrong password should be rejected
try {
    $bad_body = @{ email = "owner@demo.com"; password = "wrong" } | ConvertTo-Json
    Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method Post -ContentType "application/json" -Body $bad_body
    Write-Host "FAIL wrong password was accepted" -ForegroundColor Red
} catch {
    Write-Host "OK   wrong password correctly rejected ($($_.Exception.Response.StatusCode.value__))" -ForegroundColor Green
}