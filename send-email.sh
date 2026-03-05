#!/bin/bash
# 发送邮件脚本
# 用法: ./send-email.sh "收件人邮箱" "主题" "内容" [附件路径]

TO=$1
SUBJECT=$2
BODY=$3
ATTACHMENT=$4

if [ -z "$TO" ] || [ -z "$SUBJECT" ] || [ -z "$BODY" ]; then
    echo "用法: $0 <收件人> <主题> <内容> [附件]"
    exit 1
fi

# 如果有附件
if [ -n "$ATTACHMENT" ] && [ -f "$ATTACHMENT" ]; then
    # 使用 base64 编码附件
    FILENAME=$(basename "$ATTACHMENT")
    BOUNDARY="boundary-$(date +%s)"
    
    # 构建 multipart 邮件
    {
        echo "To: $TO"
        echo "Subject: $SUBJECT"
        echo "Content-Type: multipart/mixed; boundary=\"$BOUNDARY\""
        echo "MIME-Version: 1.0"
        echo ""
        echo "--$BOUNDARY"
        echo "Content-Type: text/plain; charset=UTF-8"
        echo ""
        echo "$BODY"
        echo ""
        echo "--$BOUNDARY"
        echo "Content-Type: application/octet-stream; name=\"$FILENAME\""
        echo "Content-Disposition: attachment; filename=\"$FILENAME\""
        echo "Content-Transfer-Encoding: base64"
        echo ""
        base64 "$ATTACHMENT"
        echo ""
        echo "--$BOUNDARY--"
    } | msmtp "$TO"
else
    # 纯文本邮件
    echo -e "Subject: $SUBJECT\n\n$BODY" | msmtp "$TO"
fi

if [ $? -eq 0 ]; then
    echo "邮件发送成功"
else
    echo "邮件发送失败"
    exit 1
fi
