# 多机压力测试启动脚本
# 使用方法：在服务器上运行此脚本，同时启动 3 台电脑的测试

$serverIp = "192.168.1.100"  # 修改为服务器实际 IP 地址
$duration = 120  # 测试持续时间（秒）
$users = 20  # 每台电脑的并发用户数

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "多机压力测试启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "服务器地址：http://$serverIp`:5000" -ForegroundColor Yellow
Write-Host "测试持续时间：$duration 秒" -ForegroundColor Yellow
Write-Host "每台电脑并发用户：$users" -ForegroundColor Yellow
Write-Host ""

# 电脑 1 - 使用 user1
Write-Host "[电脑 1] 启动测试 (user1)..." -ForegroundColor Green
Start-Process python -ArgumentList "jmeter_test.py --url http://$serverIp`:5000 --duration $duration --users $users --username user1 --password user123 --type encrypted"

# 电脑 2 - 使用 user2
Write-Host "[电脑 2] 启动测试 (user2)..." -ForegroundColor Green
Start-Process python -ArgumentList "jmeter_test.py --url http://$serverIp`:5000 --duration $duration --users $users --username user2 --password user123 --type encrypted"

# 电脑 3 - 使用 user3
Write-Host "[电脑 3] 启动测试 (user3)..." -ForegroundColor Green
Start-Process python -ArgumentList "jmeter_test.py --url http://$serverIp`:5000 --duration $duration --users $users --username user3 --password user123 --type encrypted"

Write-Host ""
Write-Host "所有测试已启动！" -ForegroundColor Cyan
Write-Host "测试结果将保存到：stress_test_results.csv" -ForegroundColor Cyan
Write-Host ""
Write-Host "按任意键查看服务器状态..." -ForegroundColor Gray
