#!/bin/bash
# 核心配置文件备份到GitHub (SSH方式)
# 每天02:22执行

set -e

WORKSPACE="/root/.openclaw/workspace"
BACKUP_DIR="/tmp/openclaw-backup-core"
DATE_STR=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$WORKSPACE/logs/backup_core.log"

mkdir -p $(dirname $LOG_FILE)

echo "========================================" >> $LOG_FILE
echo "[$(date)] 核心配置备份开始" >> $LOG_FILE

rm -rf $BACKUP_DIR
mkdir -p $BACKUP_DIR

# 克隆仓库 (SSH方式)
echo "[$(date)] 正在克隆仓库..." >> $LOG_FILE
GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no" git clone git@github.com:LionGG/claw.git $BACKUP_DIR 2>> $LOG_FILE || {
    echo "[$(date)] 克隆仓库失败" >> $LOG_FILE
    exit 1
}

# 创建配置文件目录
mkdir -p $BACKUP_DIR/core-config

# 复制核心配置文件
echo "[$(date)] 复制核心配置文件..." >> $LOG_FILE

cp -f $WORKSPACE/SOUL.md $BACKUP_DIR/core-config/ 2>/dev/null || echo "  SOUL.md 不存在" >> $LOG_FILE
cp -f $WORKSPACE/SOP.md $BACKUP_DIR/core-config/ 2>/dev/null || echo "  SOP.md 不存在" >> $LOG_FILE
cp -f $WORKSPACE/USER.md $BACKUP_DIR/core-config/ 2>/dev/null || echo "  USER.md 不存在" >> $LOG_FILE
cp -f $WORKSPACE/IDENTITY.md $BACKUP_DIR/core-config/ 2>/dev/null || echo "  IDENTITY.md 不存在" >> $LOG_FILE
cp -f $WORKSPACE/ERROR_PREVENTION.md $BACKUP_DIR/core-config/ 2>/dev/null || echo "  ERROR_PREVENTION.md 不存在" >> $LOG_FILE
cp -f $WORKSPACE/TOOLS.md $BACKUP_DIR/core-config/ 2>/dev/null || echo "  TOOLS.md 不存在" >> $LOG_FILE
cp -f $WORKSPACE/cron-jobs-final.json $BACKUP_DIR/core-config/ 2>/dev/null || echo "  cron-jobs-final.json 不存在" >> $LOG_FILE

# 记录备份信息
echo "备份时间: $(date)" > $BACKUP_DIR/core-config/BACKUP_INFO.txt
echo "备份内容: 核心配置文件" >> $BACKUP_DIR/core-config/BACKUP_INFO.txt
echo "" >> $BACKUP_DIR/core-config/BACKUP_INFO.txt
echo "文件列表:" >> $BACKUP_DIR/core-config/BACKUP_INFO.txt
ls -la $BACKUP_DIR/core-config/ >> $BACKUP_DIR/core-config/BACKUP_INFO.txt

# 进入仓库目录
cd $BACKUP_DIR

# 配置git
git config user.name "Billy"
git config user.email "billy@openclaw.ai"

# 检查是否有变更
if git diff --quiet && git diff --cached --quiet; then
    echo "[$(date)] 没有变更需要提交" >> $LOG_FILE
else
    git add -A
    git commit -m "核心配置备份 - ${DATE_STR}" -m "自动备份核心配置文件" 2>> $LOG_FILE
    GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no" git push origin main 2>> $LOG_FILE || GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no" git push origin master 2>> $LOG_FILE
    echo "[$(date)] 核心配置备份完成并推送到GitHub" >> $LOG_FILE
fi

rm -rf $BACKUP_DIR

echo "[$(date)] 备份流程结束" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

exit 0
