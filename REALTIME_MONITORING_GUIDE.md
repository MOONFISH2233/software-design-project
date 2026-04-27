# 📊 服务器实时数据监控指南

## 🎯 3种实时监控方法

### 方法1：智能监控脚本（推荐）⭐⭐⭐⭐⭐

**特点**: 
- ✅ 自动检测新数据
- ✅ 显示数据统计
- ✅ 格式化输出

**使用方法**:
```bash
ssh root@47.103.108.47
cd /root/course-project/week5/data-server/data-server
./scripts/monitor_data.sh 2  # 每2秒刷新
```

**输出示例**:
```
✅ [10:14:35] 新增 3 条数据 (总计: 595)
   📄 data_20260424_101435_129562.json:
      💧水分:61.0% | 🛢️油分:49.2% | 🌡️温度:36.2°C
   📄 data_20260424_101432_881434.json:
      💧水分:51.9% | 🛢️油分:23.2% | 🌡️温度:37.7°C
```

**停止**: 按 `Ctrl+C`

---

### 方法2：持续显示最新文件 ⭐⭐⭐⭐

**特点**:
- ✅ 只显示最新一条数据
- ✅ 完整JSON格式
- ✅ 自动刷新

**使用方法**:
```bash
ssh root@47.103.108.47
cd /root/course-project/week5/data-server/data-server

while true; do
    LATEST=$(ls -t data/*.json 2>/dev/null | head -1)
    if [ -n "$LATEST" ]; then
        clear
        echo "📄 最新文件: $(basename $LATEST)"
        echo "⏰ 更新时间: $(date)"
        echo ""
        cat $LATEST | python3 -m json.tool
    fi
    sleep 2
done
```

**输出示例**:
```json
{
    "device_id": "SIM_DEV_674",
    "sensor_type": "skin",
    "data": {
        "moisture": 67.4,
        "oiliness": 36.1,
        "temperature": 36.2
    },
    "timestamp": "2026-04-24T02:14:55.057407",
    "quality_score": 0.83
}
```

**停止**: 按 `Ctrl+C`

---

### 方法3：简洁摘要视图 ⭐⭐⭐⭐

**特点**:
- ✅ 显示最新5条数据
- ✅ 紧凑格式
- ✅ 一目了然

**使用方法**:
```bash
ssh root@47.103.108.47
cd /root/course-project/week5/data-server/data-server

while true; do
    clear
    echo '=== 最新5条数据 ==='
    date
    echo ''
    ls -t data/*.json 2>/dev/null | head -5 | while read f; do
        echo "📄 $(basename $f)"
        python3 -c "import json; d=json.load(open('$f')); print(f\"   💧{d['data'].get('moisture')}% | 🛢️{d['data'].get('oiliness')}% | 🌡️{d['data'].get('temperature')}°C\")" 2>/dev/null
    done
    sleep 3
done
```

**输出示例**:
```
=== 最新5条数据 ===
Fri Apr 24 10:15:17 AM CST 2026

📄 data_20260424_101516_179388.json
   💧67.9% | 🛢️30.5% | 🌡️35.5°C
📄 data_20260424_101516_173578.json
   💧73.2% | 🛢️37.1% | 🌡️35.5°C
📄 data_20260424_101513_925317.json
   💧50.5% | 🛢️31.2% | 🌡️37.5°C
```

**停止**: 按 `Ctrl+C`

---

## 🔧 其他常用监控命令

### 1. 查看数据统计
```bash
# 统计数据文件总数
ls /root/course-project/week5/data-server/data-server/data/*.json | wc -l

# 查看最新10个文件
ls -lht /root/course-project/week5/data-server/data-server/data/ | head -10

# 查看文件大小分布
du -sh /root/course-project/week5/data-server/data-server/data/
```

### 2. 查看特定文件内容
```bash
# 查看最新文件
cat $(ls -t /root/course-project/week5/data-server/data-server/data/*.json | head -1) | python3 -m json.tool

# 查看指定文件
cat /root/course-project/week5/data-server/data-server/data/data_20260424_101516_179388.json | python3 -m json.tool
```

### 3. 使用 MongoDB 查询（如果 module_writer 在运行）
```bash
mongosh sensor_data

# 查看记录总数
db.skin_sensor.countDocuments()

# 查看最新5条
db.skin_sensor.find().sort({timestamp: -1}).limit(5).pretty()

# 按设备ID查询
db.skin_sensor.find({device_id: "SIM_DEV_674"}).sort({timestamp: -1}).limit(3).pretty()

# 退出
exit
```

### 4. 实时监控日志
```bash
# 查看Flask应用日志
tail -f /var/log/gunicorn-flask-data-server.log

# 查看module_writer日志（如果运行）
tail -f /root/course-project/week5/data-server/data-server/logs/writer.log
```

---

## 🎬 向老师演示实时监控

### 演示步骤（2分钟）

#### Step 1: 启动本地模拟器
在本地Windows执行：
```powershell
cd "d:\学习\软件设计\data-server"
python examples/simple_simulator.py
```

#### Step 2: SSH登录服务器并启动监控
```bash
ssh root@47.103.108.47
cd /root/course-project/week5/data-server/data-server
./scripts/monitor_data.sh 2
```

#### Step 3: 展示实时数据流
指着屏幕说：
```
大家可以看到，数据正在实时上传到服务器。
每2秒钟就有一条新的传感器数据到达。

这里显示的是：
- 设备ID: SIM_DEV_674
- 水分含量: 67.9%
- 油分含量: 30.5%
- 温度: 35.5°C

这些数据会自动保存到服务器的数据目录中。
```

#### Step 4: 展示数据存储
按 `Ctrl+C` 停止监控，然后执行：
```bash
# 显示总数据量
echo "当前数据文件总数:"
ls data/*.json | wc -l

# 显示最新文件
echo ""
echo "最新数据文件:"
ls -lht data/ | head -3
```

---

## 💡 高级技巧

### 1. 后台运行监控
```bash
# 将监控输出保存到文件
nohup ./scripts/monitor_data.sh 2 > /tmp/monitor.log 2>&1 &

# 查看日志
tail -f /tmp/monitor.log
```

### 2. 监控特定设备
```bash
# 只监控特定设备ID的数据
watch -n 2 'grep -l "SIM_DEV_674" /root/course-project/week5/data-server/data-server/data/*.json | tail -5'
```

### 3. 数据统计分析
```bash
# 统计每小时数据量
ls data/*.json | awk -F'_' '{print $2"_"$3}' | cut -c1-13 | sort | uniq -c

# 计算平均水分值
python3 -c "
import json, glob, os
files = sorted(glob.glob('data/*.json'))[-100:]  # 最近100条
values = []
for f in files:
    with open(f) as fp:
        d = json.load(fp)
        values.append(d['data']['moisture'])
print(f'平均水分: {sum(values)/len(values):.1f}%')
print(f'最高水分: {max(values):.1f}%')
print(f'最低水分: {min(values):.1f}%')
"
```

---

## ❓ 常见问题

### Q1: 监控脚本没有输出？
**A**: 可能是所有文件都已被处理。重启脚本即可：
```bash
./scripts/monitor_data.sh 2
```

### Q2: 如何调整刷新频率？
**A**: 修改命令最后的数字（秒数）：
```bash
./scripts/monitor_data.sh 1  # 每1秒刷新
./scripts/monitor_data.sh 5  # 每5秒刷新
```

### Q3: 想看MongoDB中的数据怎么办？
**A**: 需要先启动 module_writer：
```bash
cd /root/course-project/week5/data-server/data-server
nohup python3 module_writer.py > logs/writer.log 2>&1 &
```

然后使用 mongosh 查询。

### Q4: 如何停止所有后台进程？
**A**: 
```bash
# 查找进程
ps aux | grep monitor

# 杀死进程
kill <PID>
```

---

## 📊 当前系统状态

| 项目 | 状态 | 说明 |
|------|------|------|
| 本地模拟器 | ✅ 运行中 | simple_simulator.py |
| 数据接收 | ✅ 正常 | Flask服务器接收HTTP请求 |
| 文件存储 | ✅ 正常 | JSON文件持续生成 |
| 实时监控 | ✅ 就绪 | 3种监控方法可用 |
| MongoDB | ⚠️ 未写入 | module_writer未启动 |

---

**现在你可以实时看到数据上传了！🎉**

选择你喜欢的方法开始监控吧！
