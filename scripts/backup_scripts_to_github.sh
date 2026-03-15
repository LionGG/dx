#!/bin/bash
# 脚本和重要文件备份到GitHub
# 每天02:22执行

set -e

WORKSPACE="/root/.openclaw/workspace"
BACKUP_DIR="/tmp/openclaw-scripts-backup"
DATE_STR=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$WORKSPACE/logs/backup_scripts.log"

mkdir -p $(dirname $LOG_FILE)

echo "========================================" >> $LOG_FILE
echo "[$(date)] 脚本备份开始" >> $LOG_FILE

rm -rf $BACKUP_DIR
mkdir -p $BACKUP_DIR

# 克隆仓库 (SSH方式)
echo "[$(date)] 克隆GitHub仓库..." >> $LOG_FILE
GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no" git clone git@github.com:LionGG/claw.git $BACKUP_DIR 2>> $LOG_FILE || {
    echo "[$(date)] 克隆失败" >> $LOG_FILE
    exit 1
}

echo "[$(date)] 复制文件到各目录..." >> $LOG_FILE

# ==================== core-scripts/ ====================
mkdir -p $BACKUP_DIR/core-scripts
cp -f $WORKSPACE/scripts/backup_core_config.sh $BACKUP_DIR/core-scripts/ 2>/dev/null || true
cp -f $WORKSPACE/scripts/comprehensive_cleanup.sh $BACKUP_DIR/core-scripts/ 2>/dev/null || true
cp -f $WORKSPACE/scripts/daily_journal_pipeline.py $BACKUP_DIR/core-scripts/ 2>/dev/null || true
cp -f $WORKSPACE/scripts/fetch_and_send_us_stock.py $BACKUP_DIR/core-scripts/ 2>/dev/null || true
cp -f $WORKSPACE/scripts/feishu_card_wrapper.py $BACKUP_DIR/core-scripts/ 2>/dev/null || true
cp -f $WORKSPACE/scripts/daily_archive.sh $BACKUP_DIR/core-scripts/ 2>/dev/null || true
cp -f $WORKSPACE/scripts/check_cron_status.sh $BACKUP_DIR/core-scripts/ 2>/dev/null || true
cp -f $WORKSPACE/scripts/eastmoney_api.py $BACKUP_DIR/core-scripts/ 2>/dev/null || true
cp -f $WORKSPACE/scripts/error_pattern_analysis.py $BACKUP_DIR/core-scripts/ 2>/dev/null || true
cp -f $WORKSPACE/scripts/error_prevention_check.py $BACKUP_DIR/core-scripts/ 2>/dev/null || true
echo "  core-scripts: $(ls $BACKUP_DIR/core-scripts/ | wc -l) 个文件" >> $LOG_FILE

# ==================== a-share/ ====================
mkdir -p $BACKUP_DIR/a-share
cp -f $WORKSPACE/stock/a-share-warehouse/scripts/calculate_ma50_ratio.py $BACKUP_DIR/a-share/ 2>/dev/null || true
cp -f $WORKSPACE/stock/dx/scripts/master_pipeline.py $BACKUP_DIR/a-share/ 2>/dev/null || true
cp -f $WORKSPACE/stock/dx/scripts/task1_data_fetch.py $BACKUP_DIR/a-share/ 2>/dev/null || true
cp -f $WORKSPACE/stock/dx/scripts/task2_analysis.py $BACKUP_DIR/a-share/ 2>/dev/null || true
cp -f $WORKSPACE/stock/dx/scripts/task3_deploy.py $BACKUP_DIR/a-share/ 2>/dev/null || true
cp -f $WORKSPACE/stock/dx/scripts/emotion_score_v7.py $BACKUP_DIR/a-share/ 2>/dev/null || true
cp -f $WORKSPACE/stock/dx/scripts/feishu_notifier.py $BACKUP_DIR/a-share/ 2>/dev/null || true
cp -f $WORKSPACE/stock/dx/scripts/crawler.py $BACKUP_DIR/a-share/ 2>/dev/null || true
cp -f $WORKSPACE/stock/dx/scripts/deploy.py $BACKUP_DIR/a-share/ 2>/dev/null || true
cp -f $WORKSPACE/stock/dx/scripts/publish_to_mowen.py $BACKUP_DIR/a-share/ 2>/dev/null || true
cp -f $WORKSPACE/stock/dx/data/duanxian.db $BACKUP_DIR/a-share/ 2>/dev/null || true
echo "  a-share: $(ls $BACKUP_DIR/a-share/ | wc -l) 个文件" >> $LOG_FILE

# ==================== stock-plan/ ====================
mkdir -p $BACKUP_DIR/stock-plan
mkdir -p $BACKUP_DIR/stock-plan/skills/portfolio-parser/scripts
cp -f $WORKSPACE/stock-plan/trade_service.py $BACKUP_DIR/stock-plan/ 2>/dev/null || true
cp -f $WORKSPACE/stock-plan/agents/trade-assistant/core.py $BACKUP_DIR/stock-plan/ 2>/dev/null || true
cp -f $WORKSPACE/stock-plan/agents/trade-assistant/parser.py $BACKUP_DIR/stock-plan/ 2>/dev/null || true
cp -f $WORKSPACE/stock-plan/agents/trade-assistant/save_plan.py $BACKUP_DIR/stock-plan/ 2>/dev/null || true
cp -f $WORKSPACE/stock-plan/agents/trade-assistant/cli.py $BACKUP_DIR/stock-plan/ 2>/dev/null || true
cp -f $WORKSPACE/stock-plan/scripts/init_portfolio_db.py $BACKUP_DIR/stock-plan/ 2>/dev/null || true
cp -f $WORKSPACE/stock-plan/scripts/query_portfolio.py $BACKUP_DIR/stock-plan/ 2>/dev/null || true
cp -f $WORKSPACE/stock-plan/scripts/market_context.py $BACKUP_DIR/stock-plan/ 2>/dev/null || true
cp -f $WORKSPACE/stock-plan/scripts/import_historical_data.py $BACKUP_DIR/stock-plan/ 2>/dev/null || true
cp -f $WORKSPACE/skills/portfolio-parser/scripts/portfolio_parser.py $BACKUP_DIR/stock-plan/skills/portfolio-parser/scripts/ 2>/dev/null || true
cp -f $WORKSPACE/docs/laorer-trade-assistant.md $BACKUP_DIR/stock-plan/ 2>/dev/null || true
echo "  stock-plan: $(ls $BACKUP_DIR/stock-plan/*.py 2>/dev/null | wc -l) 个脚本" >> $LOG_FILE

# ==================== etf-indicators/ ====================
mkdir -p $BACKUP_DIR/etf-indicators
cp -f $WORKSPACE/projects/etf-indicators/scripts/batch_calc_etf.py $BACKUP_DIR/etf-indicators/ 2>/dev/null || true
cp -f $WORKSPACE/projects/etf-indicators/scripts/calc_etf_full_v52.py $BACKUP_DIR/etf-indicators/ 2>/dev/null || true
cp -f $WORKSPACE/projects/etf-indicators/scripts/calc_etf_trend_v52.py $BACKUP_DIR/etf-indicators/ 2>/dev/null || true
cp -f $WORKSPACE/projects/etf-indicators/scripts/cheese_batch_final.py $BACKUP_DIR/etf-indicators/ 2>/dev/null || true
cp -f $WORKSPACE/projects/etf-indicators/scripts/calculate_rs.py $BACKUP_DIR/etf-indicators/ 2>/dev/null || true
cp -f $WORKSPACE/projects/etf-indicators/scripts/cheese_background.py $BACKUP_DIR/etf-indicators/ 2>/dev/null || true
cp -f $WORKSPACE/projects/etf-indicators/scripts/backfill_volatility.py $BACKUP_DIR/etf-indicators/ 2>/dev/null || true
cp -f $WORKSPACE/projects/etf-indicators/scripts/backfill_volume_strength.py $BACKUP_DIR/etf-indicators/ 2>/dev/null || true
cp -f $WORKSPACE/projects/etf-indicators/scripts/cheese_api_probe.py $BACKUP_DIR/etf-indicators/ 2>/dev/null || true
cp -f $WORKSPACE/projects/etf-indicators/scripts/batch_optimized_v2.py $BACKUP_DIR/etf-indicators/ 2>/dev/null || true
cp -f $WORKSPACE/projects/etf-indicators/scripts/db_config.py $BACKUP_DIR/etf-indicators/ 2>/dev/null || true
cp -f $WORKSPACE/projects/etf-indicators/scripts/README.md $BACKUP_DIR/etf-indicators/ 2>/dev/null || true
echo "  etf-indicators: $(ls $BACKUP_DIR/etf-indicators/ | wc -l) 个文件" >> $LOG_FILE

# ==================== docs/ ====================
mkdir -p $BACKUP_DIR/docs
cp -f $WORKSPACE/HEARTBEAT.md $BACKUP_DIR/docs/ 2>/dev/null || true
cp -f $WORKSPACE/TASK_EXECUTION.md $BACKUP_DIR/docs/ 2>/dev/null || true
echo "  docs: $(ls $BACKUP_DIR/docs/ | wc -l) 个文件" >> $LOG_FILE

# ==================== memory/ ====================
mkdir -p $BACKUP_DIR/memory
cp -f $WORKSPACE/MEMORY.md $BACKUP_DIR/memory/ 2>/dev/null || true
echo "  memory: $(ls $BACKUP_DIR/memory/ | wc -l) 个文件" >> $LOG_FILE

# ==================== wal/ (写前日志) ====================
mkdir -p $BACKUP_DIR/wal
cp -f $WORKSPACE/.wal/decisions.md $BACKUP_DIR/wal/ 2>/dev/null || true
cp -f $WORKSPACE/.wal/corrections.md $BACKUP_DIR/wal/ 2>/dev/null || true
cp -f $WORKSPACE/.wal/details.md $BACKUP_DIR/wal/ 2>/dev/null || true
echo "  wal: $(ls $BACKUP_DIR/wal/ | wc -l) 个文件" >> $LOG_FILE

# ==================== archive/ (归档旧文档) ====================
mkdir -p $BACKUP_DIR/archive
cp -f $WORKSPACE/AGENTS.md $BACKUP_DIR/archive/ 2>/dev/null || true
cp -f $WORKSPACE/BOOTSTRAP.md $BACKUP_DIR/archive/ 2>/dev/null || true
cp -f $WORKSPACE/CHECKLIST.md $BACKUP_DIR/archive/ 2>/dev/null || true
cp -f $WORKSPACE/EXECUTION_ENFORCEMENT.md $BACKUP_DIR/archive/ 2>/dev/null || true
cp -f $WORKSPACE/ONBOARDING.md $BACKUP_DIR/archive/ 2>/dev/null || true
cp -f $WORKSPACE/SESSION-STATE.md $BACKUP_DIR/archive/ 2>/dev/null || true
echo "  archive: $(ls $BACKUP_DIR/archive/ | wc -l) 个文件" >> $LOG_FILE

# 记录备份信息
echo "" > $BACKUP_DIR/BACKUP_INFO_SCRIPTS.txt
echo "脚本备份时间: $(date)" >> $BACKUP_DIR/BACKUP_INFO_SCRIPTS.txt
echo "备份内容: 核心脚本和重要文件" >> $BACKUP_DIR/BACKUP_INFO_SCRIPTS.txt
echo "" >> $BACKUP_DIR/BACKUP_INFO_SCRIPTS.txt
echo "目录结构:" >> $BACKUP_DIR/BACKUP_INFO_SCRIPTS.txt
find $BACKUP_DIR -type f -not -path "*/.git/*" | sort >> $BACKUP_DIR/BACKUP_INFO_SCRIPTS.txt

# Git提交
cd $BACKUP_DIR
git config user.name "Billy"
git config user.email "billy@openclaw.ai"

if git diff --quiet && git diff --cached --quiet; then
    echo "[$(date)] 没有变更需要提交" >> $LOG_FILE
else
    git add -A
    git commit -m "脚本备份 - ${DATE_STR}" -m "自动备份核心脚本和重要文件" 2>> $LOG_FILE
    GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no" git push origin main 2>> $LOG_FILE || GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no" git push origin master 2>> $LOG_FILE
    echo "[$(date)] 脚本备份完成并推送到GitHub" >> $LOG_FILE
fi

rm -rf $BACKUP_DIR

echo "[$(date)] 备份流程结束" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

exit 0
