# Flask 数据服务器 - API 接口文档

## 接口列表

### 1. 数据接收接口

| 属性 | 说明 |
|------|------|
| **接口地址** | `/api/receive` |
| **请求方式** | POST |
| **数据格式** | JSON / Form |
| **传输频率** | 实时/按需（建议间隔≥1 秒） |

**请求参数：**

| 参数名称 | 类型 | 必填 | 说明 | 示例 |
|----------|------|------|------|------|
| data | Object | 是 | 要传输的数据对象 | `{"temperature": 25.5}` |
| description | String | 否 | 数据描述 | "环境传感器数据" |
| source | String | 否 | 数据来源 | "local" / "cloud_sync" |
| upload_time | String | 否 | 上传时间（ISO 格式） | "2026-03-22T15:30:00" |

**响应示例：**
```json
{
  "status": "success",
  "message": "数据接收成功",
  "filename": "data_20260322_153000_123456.json",
  "timestamp": "2026-03-22T15:30:00"
}
```

---

### 2. 健康检查接口

| 属性 | 说明 |
|------|------|
| **接口地址** | `/api/health` |
| **请求方式** | GET |
| **数据格式** | JSON |
| **传输频率** | 定期检测（建议间隔 30 秒） |

**请求参数：** 无

**响应示例：**
```json
{
  "status": "healthy",
  "service": "Flask Data Server",
  "timestamp": "2026-03-22T15:30:00"
}
```

---

### 3. 日志查询接口

| 属性 | 说明 |
|------|------|
| **接口地址** | `/api/logs` |
| **请求方式** | GET |
| **数据格式** | JSON |
| **传输频率** | 按需（建议间隔≥5 秒） |

**请求参数：** 无

**响应示例：**
```json
{
  "logs": "2026-03-22 15:30:00 - INFO - 成功接收并保存数据...\n...",
  "file": "server_20260322.log"
}
```

---

## 数据传输频率建议

| 场景 | 建议频率 | 说明 |
|------|----------|------|
| 传感器数据上传 | 每 5-60 秒 | 根据传感器精度需求 |
| 日志同步 | 每 5-10 分钟 | 批量传输更高效 |
| 健康检查 | 每 30 秒 | 快速发现服务异常 |
| 文件上传 | 按需 | 避免并发上传 |
| 云端同步 | 每 1-5 分钟 | 根据数据重要性调整 |

---

## 使用示例

### Python 客户端
```python
import requests

# 上传数据
data = {
    "temperature": 25.5,
    "humidity": 60,
    "device_id": "sensor_001"
}

response = requests.post(
    'http://47.103.108.47:5000/api/receive',
    json=data
)

print(response.json())
```

### cURL 命令
```bash
# 上传数据
curl -X POST http://47.103.108.47:5000/api/receive \
  -H "Content-Type: application/json" \
  -d '{"temperature": 25.5, "humidity": 60}'

# 健康检查
curl http://47.103.108.47:5000/api/health

# 查看日志
curl http://47.103.108.47:5000/api/logs
```

---

## 错误码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 500 | 服务器内部错误 |

---

## 文件结构

```
data-server/
── app.py                 # Flask 服务器主程序
├── requirements.txt       # Python 依赖
├── local_to_cloud.py     # 本地到云端传输客户端
├── cloud_to_cloud.py     # 云端到云端传输客户端
├── deploy.sh             # 部署脚本
├── Jenkinsfile           # Jenkins 配置
├── logs/                 # 日志目录
│   └── server_YYYYMMDD.log
└── data/                 # 数据文件目录
    └── data_YYYYMMDD_HHMMSS_ffffff.json
```
