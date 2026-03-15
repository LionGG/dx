#!/bin/bash
# 短线情绪研判 - 强制执行检查清单
# 执行前必须先通过此检查，不通过禁止执行

SCRIPT_DIR="/root/.openclaw/workspace/stock/dx"
DB_FILE="$SCRIPT_DIR/data/duanxian.db"

echo "=========================================="
echo "短线情绪研判 - 强制执行检查清单"
echo "=========================================="
echo ""

FAILED=0

# 检查1: 数据库可访问
echo "[检查1/10] 数据库可访问..."
if [ -f "$DB_FILE" ]; then
    echo "  ✅ 数据库文件存在"
else
    echo "  ❌ 数据库文件不存在"
    FAILED=1
fi

# 检查2: 最新日期
echo "[检查2/10] 最新日期..."
LATEST_DATE=$(sqlite3 "$DB_FILE" "SELECT MAX(date) FROM market_sentiment;")
echo "  ✅ 最新日期: $LATEST_DATE"

# 检查3: 情绪数据完整
echo "[检查3/10] 情绪数据完整..."
COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM market_sentiment WHERE date = '$LATEST_DATE';")
if [ "$COUNT" -eq 1 ]; then
    echo "  ✅ 情绪数据存在"
else
    echo "  ❌ 情绪数据缺失"
    FAILED=1
fi

# 检查4: 指数数据完整
echo "[检查4/10] 指数数据完整..."
INDEX_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM index_kline WHERE date = '$LATEST_DATE';")
if [ "$INDEX_COUNT" -ge 2 ]; then
    echo "  ✅ 指数数据存在 ($INDEX_COUNT 条)"
else
    echo "  ⚠️  指数数据缺失 ($INDEX_COUNT 条)"
    # 不强制失败，但警告
fi

# 检查5: 星期几计算
echo "[检查5/10] 星期几计算..."
WEEKDAY=$(python3 -c "from datetime import datetime; d = datetime.strptime('$LATEST_DATE', '%Y-%m-%d'); print(['周一','周二','周三','周四','周五','周六','周日'][d.weekday()])")
echo "  ✅ $LATEST_DATE 是: $WEEKDAY"

# 检查6: 关键字段不为空
echo "[检查6/10] 关键字段检查..."
SENTIMENT=$(sqlite3 "$DB_FILE" "SELECT sentiment_index FROM market_sentiment WHERE date = '$LATEST_DATE';")
LIMIT_UP=$(sqlite3 "$DB_FILE" "SELECT limit_up FROM market_sentiment WHERE date = '$LATEST_DATE';")
LIMIT_DOWN=$(sqlite3 "$DB_FILE" "SELECT limit_down FROM market_sentiment WHERE date = '$LATEST_DATE';")

if [ -n "$SENTIMENT" ] && [ -n "$LIMIT_UP" ] && [ -n "$LIMIT_DOWN" ]; then
    echo "  ✅ 情绪指数: $SENTIMENT"
    echo "  ✅ 涨停/跌停: $LIMIT_UP/$LIMIT_DOWN"
else
    echo "  ❌ 关键字段为空"
    FAILED=1
fi

# 检查7: 报告模板存在
echo "[检查7/10] 报告模板..."
if [ -f "$SCRIPT_DIR/TASK_DX_FINAL.md" ]; then
    echo "  ✅ 任务文档存在"
else
    echo "  ❌ 任务文档缺失"
    FAILED=1
fi

# 检查8: 脚本存在
echo "[检查8/10] 执行脚本..."
for script in update_html_data.py deploy.py; do
    if [ -f "$SCRIPT_DIR/scripts/$script" ]; then
        echo "  ✅ $script 存在"
    else
        echo "  ❌ $script 缺失"
        FAILED=1
    fi
done

echo ""
echo "=========================================="
if [ $FAILED -eq 0 ]; then
    echo "✅ 所有检查通过，可以执行"
    echo "=========================================="
    exit 0
else
    echo "❌ 检查未通过，禁止执行"
    echo "=========================================="
    exit 1
fi
