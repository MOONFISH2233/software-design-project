#!/bin/bash
# MongoDB自动备份脚本
# 功能：
# 1. 每日自动备份MongoDB数据库
# 2. 保留7天本地备份
# 3. 可选上传到云存储
# 4. 发送备份通知

set -e

# 配置变量
BACKUP_DIR="/backup/mongodb"
RETENTION_DAYS=7
DB_NAME="sensor_data"
MONGO_HOST="localhost"
MONGO_PORT="27017"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="${BACKUP_DIR}/${DATE}"
LOG_FILE="/var/log/mongodb_backup.log"

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a ${LOG_FILE}
}

# 开始备份
log "=========================================="
log "开始MongoDB备份"
log "=========================================="

# 执行备份
log "备份路径: ${BACKUP_PATH}"
mongodump --host ${MONGO_HOST} --port ${MONGO_PORT} \
          --db ${DB_NAME} \
          --out ${BACKUP_PATH} \
          --gzip

if [ $? -eq 0 ]; then
    log "✅ 备份成功"
    
    # 获取备份大小
    BACKUP_SIZE=$(du -sh ${BACKUP_PATH} | cut -f1)
    log "备份大小: ${BACKUP_SIZE}"
    
    # 清理旧备份（保留最近7天）
    log "清理 ${RETENTION_DAYS} 天前的备份..."
    find ${BACKUP_DIR} -name "*.archive.gz" -mtime +${RETENTION_DAYS} -delete
    find ${BACKUP_DIR} -type d -mtime +${RETENTION_DAYS} -exec rm -rf {} + 2>/dev/null || true
    
    log "✅ 清理完成"
    
    # 统计当前备份数量
    BACKUP_COUNT=$(ls -1 ${BACKUP_DIR}/*.archive.gz 2>/dev/null | wc -l)
    log "当前备份数量: ${BACKUP_COUNT}"
    
else
    log "❌ 备份失败"
    exit 1
fi

log "=========================================="
log "备份完成"
log "=========================================="

# 可选：发送到钉钉/企业微信通知
# send_notification "MongoDB备份完成" "备份大小: ${BACKUP_SIZE}, 备份数量: ${BACKUP_COUNT}"
