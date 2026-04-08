@echo off
REM ====================================
REM 手动测试 API 接口
REM ====================================

echo.
echo ======================================================================
echo                      cURL API 手动测试
echo ======================================================================
echo.

set SERVER_URL=%1
if "%SERVER_URL%"=="" set SERVER_URL=http://localhost:5000

echo 服务器地址：%SERVER_URL%
echo.
echo 请选择要测试的接口:
echo.
echo [1] 健康检查 (GET /api/health)
echo [2] 统计信息 (GET /api/stats)
echo [3] 日志查询 (GET /api/logs)
echo [4] 通用数据接收 (POST /api/receive)
echo [5] 皮肤传感器 (POST /api/sensor/skin)
echo [6] 环境传感器 (POST /api/sensor/environment)
echo [7] 设备状态 (POST /api/device/status)
echo [8] 完整测试流程
echo [0] 退出
echo.
set /p choice=请输入选择 (0-8): 

if "%choice%"=="1" goto health
if "%choice%"=="2" goto stats
if "%choice%"=="3" goto logs
if "%choice%"=="4" goto receive
if "%choice%"=="5" goto skin
if "%choice%"=="6" goto env
if "%choice%"=="7" goto device
if "%choice%"=="8" goto full_test
if "%choice%"=="0" exit /b
goto menu

:health
echo.
echo === 健康检查 ===
curl -s %SERVER_URL%/api/health | python -m json.tool
goto end

:stats
echo.
echo === 统计信息 ===
curl -s %SERVER_URL%/api/stats | python -m json.tool
goto end

:logs
echo.
echo === 日志查询 ===
curl -s %SERVER_URL%/api/logs | python -m json.tool
goto end

:receive
echo.
echo === 通用数据接收 ===
curl -X POST -H "Content-Type: application/json" ^
  -d "{\"data\":{\"test\":\"value\"},\"description\":\"测试数据\"}" ^
  %SERVER_URL%/api/receive | python -m json.tool
goto end

:skin
echo.
echo === 皮肤传感器数据 ===
curl -X POST -H "Content-Type: application/json" ^
  -d "{\"moisture\":65,\"oiliness\":35,\"device_id\":\"sensor_001\"}" ^
  %SERVER_URL%/api/sensor/skin | python -m json.tool
goto end

:env
echo.
echo === 环境传感器数据 ===
curl -X POST -H "Content-Type: application/json" ^
  -d "{\"humidity\":55,\"light_lux\":650,\"temperature\":25.5}" ^
  %SERVER_URL%/api/sensor/environment | python -m json.tool
goto end

:device
echo.
echo === 设备状态数据 ===
curl -X POST -H "Content-Type: application/json" ^
  -d "{\"device_id\":\"dev_001\",\"status\":\"online\"}" ^
  %SERVER_URL%/api/device/status | python -m json.tool
goto end

:full_test
echo.
echo === 完整测试流程 ===
echo.
echo 1. 健康检查...
curl -s %SERVER_URL%/api/health
echo.
echo.
echo 2. 上传皮肤传感器数据...
curl -X POST -H "Content-Type: application/json" ^
  -d "{\"moisture\":65,\"oiliness\":35}" ^
  %SERVER_URL%/api/sensor/skin
echo.
echo.
echo 3. 上传环境传感器数据...
curl -X POST -H "Content-Type: application/json" ^
  -d "{\"humidity\":55,\"light_lux\":650}" ^
  %SERVER_URL%/api/sensor/environment
echo.
echo.
echo 4. 查看统计信息...
curl -s %SERVER_URL%/api/stats
echo.
goto end

:menu
echo 无效的选择！
pause
goto :EOF

:end
echo.
echo ======================================================================
echo 测试完成
echo ======================================================================
echo.
pause
