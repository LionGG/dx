#!/usr/bin/env python3
"""
Webhook 服务 - 接收 HTTP 推送并转发到飞书
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import requests

# 配置
WEBHOOK_PORT = 8080
FEISHU_WEBHOOK_URL = os.environ.get('FEISHU_WEBHOOK_URL', '')

class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # 简化日志输出
        print(f"[{self.log_date_time_string()}] {args[0]}")
    
    def do_GET(self):
        """处理 GET 请求 - 健康检查"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {"status": "ok", "message": "Webhook service is running"}
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """处理 POST 请求 - 接收推送并转发到飞书"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # 读取请求体
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {"raw_text": body}
        
        # 路由处理
        if path == '/webhook/feishu':
            self.handle_feishu_webhook(data)
        elif path == '/webhook/trade':
            self.handle_trade_notification(data)
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def handle_feishu_webhook(self, data):
        """通用飞书推送"""
        message = data.get('message', data.get('text', str(data)))
        title = data.get('title', 'Webhook 通知')
        
        success = self.send_to_feishu(title, message)
        
        self.send_response(200 if success else 500)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "success": success,
            "message": "Notification sent" if success else "Failed to send"
        }).encode())
    
    def handle_trade_notification(self, data):
        """交易通知专用处理"""
        action = data.get('action', '未知操作')  # buy/sell
        stock_code = data.get('stock_code', '')
        stock_name = data.get('stock_name', '')
        price = data.get('price', 0)
        quantity = data.get('quantity', 0)
        account = data.get('account', '')
        timestamp = data.get('timestamp', '')
        notes = data.get('notes', '')
        
        # 构建消息
        emoji = "🟢" if action == "buy" else "🔴" if action == "sell" else "⚪"
        title = f"{emoji} 交易提醒：{action.upper()} {stock_name}"
        
        message_lines = [
            f"**股票**: {stock_name} ({stock_code})",
            f"**操作**: {action.upper()}",
            f"**价格**: ¥{price}",
            f"**数量**: {quantity}",
            f"**金额**: ¥{price * quantity:.2f}",
        ]
        
        if account:
            message_lines.append(f"**账户**: {account}")
        if timestamp:
            message_lines.append(f"**时间**: {timestamp}")
        if notes:
            message_lines.append(f"**备注**: {notes}")
        
        message = "\n".join(message_lines)
        
        success = self.send_to_feishu(title, message)
        
        self.send_response(200 if success else 500)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "success": success,
            "message": "Trade notification sent" if success else "Failed to send"
        }).encode())
    
    def send_to_feishu(self, title, message):
        """发送消息到飞书 - 通过写入通知文件，由主进程处理"""
        try:
            from datetime import datetime
            
            # 构建消息内容
            full_message = f"**{title}**\n\n{message}"
            
            # 写入通知队列文件
            notify_dir = "/root/.openclaw/workspace/webhook_logs/notifications"
            os.makedirs(notify_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            notify_file = f"{notify_dir}/notify_{timestamp}.json"
            
            notification = {
                "timestamp": timestamp,
                "title": title,
                "message": message,
                "full_message": full_message,
                "channel": "feishu"
            }
            
            with open(notify_file, 'w', encoding='utf-8') as f:
                json.dump(notification, f, ensure_ascii=False, indent=2)
            
            print(f"Notification queued: {notify_file}")
            return True
            
        except Exception as e:
            print(f"Error queuing notification: {e}")
            # 备用：写入日志文件
            self.log_to_file(title, message)
            return False
    
    def log_to_file(self, title, message):
        """备用：写入本地日志"""
        log_dir = "/root/.openclaw/workspace/webhook_logs"
        os.makedirs(log_dir, exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f"{log_dir}/webhook_{timestamp}.txt"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Title: {title}\n")
            f.write(f"Time: {datetime.now().isoformat()}\n")
            f.write(f"Message:\n{message}\n")

def run_server(port=WEBHOOK_PORT):
    """启动 webhook 服务"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, WebhookHandler)
    print(f"Webhook server running on port {port}")
    print(f"Endpoints:")
    print(f"  GET  /           - Health check")
    print(f"  POST /webhook/feishu  - Generic Feishu notification")
    print(f"  POST /webhook/trade   - Trade notification")
    httpd.serve_forever()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else WEBHOOK_PORT
    run_server(port)
