$base = "http://localhost:8000"

function Login($email, $password) {
    $body = @{ email = $email; password = $password } | ConvertTo-Json
    $r = Invoke-RestMethod -Uri "$base/auth/login" -Method Post -ContentType "application/json" -Body $body
    return @{ Authorization = "Bearer $($r.access_token)" }
}

$wh = Login "warehouse@demo.com" "Demo@12345"
$sales = Login "sales@demo.com" "Demo@12345"

Write-Host "`n--- Inventory (seeded) ---" -ForegroundColor Cyan
Invoke-RestMethod -Uri "$base/inventory" -Headers $wh | Format-Table product_name, sku, quantity_on_hand, reorder_point

Write-Host "`n--- Customers (seeded) ---" -ForegroundColor Cyan
$customer = (Invoke-RestMethod -Uri "$base/customers" -Headers $sales)[0]
Write-Host "Using customer: $($customer.name) (id=$($customer.id))"

Write-Host "`n--- Create an OFFLINE order request ---" -ForegroundColor Cyan
$product = (Invoke-RestMethod -Uri "$base/products" -Headers $sales)[0]
$reqBody = @{ source = "OFFLINE"; raw_text = "Customer called asking for 5 $($product.name)" } | ConvertTo-Json
$orderRequest = Invoke-RestMethod -Uri "$base/order-requests" -Method Post -ContentType "application/json" -Body $reqBody -Headers $sales
Write-Host "Created $($orderRequest.request_number), status=$($orderRequest.review_status)"

Write-Host "`n--- Approve it into an Order ---" -ForegroundColor Cyan
$approveBody = @{ customer_id = $customer.id; items = @(@{ product_id = $product.id; quantity = 5 }) } | ConvertTo-Json
$order = Invoke-RestMethod -Uri "$base/order-requests/$($orderRequest.id)/approve" -Method Post -ContentType "application/json" -Body $approveBody -Headers $sales
Write-Host "Order $($order.order_number) created - total: $($order.total), status: $($order.status)"

Write-Host "`n--- Re-approve (should be idempotent, same order number) ---" -ForegroundColor Cyan
$order2 = Invoke-RestMethod -Uri "$base/order-requests/$($orderRequest.id)/approve" -Method Post -ContentType "application/json" -Body $approveBody -Headers $sales
if ($order2.order_number -eq$order.order_number) {
    Write-Host "OK - idempotent, no duplicate order created" -ForegroundColor Green
} else {
    Write-Host "FAIL - got a different order on re-approve!" -ForegroundColor Red
}
