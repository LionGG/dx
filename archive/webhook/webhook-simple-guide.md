# 交易提醒 Webhook - 飞书群机器人方案（极简版）

## 架构
```
交易系统 → 云服务器(Webhook+群机器人) → 飞书群聊
```

---

## 第一步：创建飞书群机器人

1. 打开飞书，进入要接收提醒的群聊
2. 点击右上角 **"..."** → **群设置** → **群机器人**
3. 点击 **添加机器人** → 选择 **自定义机器人**
4. 给机器人起个名字（如"交易提醒"）
5. **复制 Webhook 地址**（格式：`https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxx`）

---

## 第二步：云服务器部署

### 1. 安装依赖
```bash
apt update
apt install -y python3 python3-pip nginx
pip3 install flask requests gunicorn
```

### 2. 创建 Webhook 服务

```bash
mkdir -p /opt/webhook
cat > /opt/webhook/app.py << 'EOF'
from flask import Flask, request
import requests

app = Flask(__name__)

# ========== 修改这里：填入你的群机器人 Webhook 地址 ==========
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxxxxxx"

def send_feishu(text):
    requests.post(FEISHU_WEBHOOK, json={"msg_type": "text", "content": {"text": text}})

@app.route('/webhook/trade', methods=['POST'])
def trade():
    data = request.json
    emoji = "🟢" if data.get('action') == 'buy' else "🔴"
    msg = f"{emoji} 交易提醒\n\n股票: {data.get('stock_name')}({data.get('stock_code')})\n操作: {data.get('action').upper()}\n价格: ¥{data.get('price')}\n数量: {data.get('quantity')}"
    send_feishu(msg)
    return {"success": True}

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
EOF
```

### 3. 启动服务
```bash
cd /opt/webhook
nohup python3 app.py > app.log 2>&1 &
```

### 4. 配置 Nginx
```bash
cat > /etc/nginx/sites-available/webhook << 'EOF'
server {
    listen 80;
    server_name webhook.yourdomain.com;
    location / {
        proxy_pass http://127.0.0.1:5000;
    }
}
EOF
ln -s /etc/nginx/sites-available/webhook /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

### 5. 申请 HTTPS 证书
```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d webhook.yourdomain.com
```

---

## 第三步：测试

```bash
curl -X POST https://webhook.yourdomain.com/webhook/trade \
  -H "Content-Type: application/json" \
  -d '{"action":"buy","stock_code":"601888","stock_name":"中国中免","price":85.50,"quantity":100}'
```

飞书群应收到消息。

---

## 第四步：接入交易系统

```python
import requests

WEBHOOK_URL = "https://webhook.yourdomain.com/webhook/trade"

def notify(action, code, name, price, qty):
    requests.post(WEBHOOK_URL, json={
        "action": action,
        "stock_code": code,
        "stock_name": name,
        "price": price,
        "quantity": qty
    })

# 使用
notify("buy", "601888", "中国中免", 85.50, 100)
```

---

## 完成

只需修改一处：`FEISHU_WEBHOOK` 填入你的群机器人地址。
