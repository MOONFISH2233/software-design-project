# PowerShell 上传脚本
# 将项目文件上传到阿里云服务器

$ServerHost = "47.103.108.47"
$ServerUser = "root"
$ProjectDir = "d:\学习\软件设计\data-server"
$RemoteDir = "/root/data-server"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Flask 数据服务器 - 文件上传工具" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 文件列表
$files = @(
    "app.py",
    "requirements.txt",
    "local_to_cloud.py",
    "cloud_to_cloud.py",
    "deploy.sh",
    "Jenkinsfile",
    "API 文档.md",
    "README.md"
)

Write-Host "准备上传以下文件:" -ForegroundColor Yellow
foreach ($file in $files) {
    Write-Host "  - $file"
}
Write-Host ""

# 检查 SSH 连接
Write-Host "检查服务器连接..." -ForegroundColor Yellow
try {
    $testConnection = Test-Connection -ComputerName $ServerHost -Count 1 -Quiet
    if ($testConnection) {
        Write-Host "✓ 服务器连接正常" -ForegroundColor Green
    } else {
        Write-Host "✗ 无法连接到服务器，请检查网络" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ 连接测试失败：$_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  请选择上传方式:" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. 使用 SCP 上传（需要 SSH 密钥或密码）"
Write-Host "  2. 手动上传说明"
Write-Host "  3. 退出"
Write-Host ""

$choice = Read-Host "请输入选项 (1-3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "开始上传文件..." -ForegroundColor Yellow
        
        # 创建远程目录
        Write-Host "创建远程目录：$RemoteDir"
        ssh ${ServerUser}@${ServerHost} "mkdir -p $RemoteDir"
        
        # 上传每个文件
        foreach ($file in $files) {
            $localPath = Join-Path $ProjectDir $file
            if (Test-Path $localPath) {
                Write-Host "  上传：$file ..." -NoNewline
                scp "$localPath" "${ServerUser}@${ServerHost}:${RemoteDir}/"
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✓" -ForegroundColor Green
                } else {
                    Write-Host "✗ 失败" -ForegroundColor Red
                }
            } else {
                Write-Host "  跳过：$file (文件不存在)" -ForegroundColor Gray
            }
        }
        
        Write-Host ""
        Write-Host "=========================================" -ForegroundColor Cyan
        Write-Host "  上传完成！" -ForegroundColor Green
        Write-Host "=========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "下一步操作:" -ForegroundColor Yellow
        Write-Host "  1. SSH 登录服务器：ssh root@$ServerHost"
        Write-Host "  2. 进入目录：cd $RemoteDir"
        Write-Host "  3. 安装依赖：pip3 install -r requirements.txt"
        Write-Host "  4. 启动服务：nohup python3 app.py > server.log 2>&1 &"
        Write-Host "  5. 查看日志：tail -f server.log"
        Write-Host ""
    }
    
    "2" {
        Write-Host ""
        Write-Host "=========================================" -ForegroundColor Cyan
        Write-Host "  手动上传步骤:" -ForegroundColor Yellow
        Write-Host "=========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "方法 1: 使用 WinSCP 或 FileZilla" -ForegroundColor Green
        Write-Host "  1. 下载 WinSCP: https://winscp.net/"
        Write-Host "  2. 主机名：$ServerHost"
        Write-Host "  3. 用户名：root"
        Write-Host "  4. 密码：你设置的密码"
        Write-Host "  5. 上传所有文件到：$RemoteDir"
        Write-Host ""
        
        Write-Host "方法 2: 使用 Git（推荐）" -ForegroundColor Green
        Write-Host "  1. 在本地初始化 Git 仓库"
        Write-Host "  2. 提交代码到 GitHub/Gitee"
        Write-Host "  3. 在服务器上使用 git clone 拉取代码"
        Write-Host ""
        Write-Host "  命令示例:" -ForegroundColor Gray
        Write-Host "  # 本地执行:" -ForegroundColor Gray
        Write-Host "  cd $ProjectDir" -ForegroundColor Gray
        Write-Host "  git init" -ForegroundColor Gray
        Write-Host "  git add ." -ForegroundColor Gray
        Write-Host "  git commit -m 'initial commit'" -ForegroundColor Gray
        Write-Host "  git remote add origin <你的仓库地址>" -ForegroundColor Gray
        Write-Host "  git push -u origin main" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  # 服务器执行:" -ForegroundColor Gray
        Write-Host "  cd /root" -ForegroundColor Gray
        Write-Host "  git clone <你的仓库地址> data-server" -ForegroundColor Gray
        Write-Host ""
        
        Write-Host "方法 3: 使用宝塔面板文件管理" -ForegroundColor Green
        Write-Host "  1. 登录宝塔面板"
        Write-Host "  2. 进入文件管理"
        Write-Host "  3. 导航到 /root/data-server"
        Write-Host "  4. 点击上传按钮"
        Write-Host ""
    }
    
    "3" {
        Write-Host "已退出" -ForegroundColor Yellow
        exit 0
    }
    
    default {
        Write-Host "无效的选项" -ForegroundColor Red
    }
}
