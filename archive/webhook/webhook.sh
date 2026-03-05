#!/bin/bash
# Webhook 服务启动脚本

PID_FILE="/tmp/webhook_server.pid"
LOG_FILE="/root/.openclaw/workspace/webhook_logs/server.log"

mkdir -p /root/.openclaw/workspace/webhook_logs

case "$1" in
  start)
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
      echo "Webhook server is already running (PID: $(cat $PID_FILE))"
      exit 1
    fi
    
    echo "Starting webhook server..."
    nohup python3 /root/.openclaw/workspace/webhook_server.py 8080 > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "Webhook server started on port 8080 (PID: $!)"
    echo "Logs: $LOG_FILE"
    ;;
    
  stop)
    if [ -f "$PID_FILE" ]; then
      PID=$(cat "$PID_FILE")
      if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping webhook server (PID: $PID)..."
        kill "$PID"
        rm -f "$PID_FILE"
        echo "Stopped."
      else
        echo "Webhook server is not running"
        rm -f "$PID_FILE"
      fi
    else
      echo "PID file not found"
    fi
    ;;
    
  status)
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
      echo "Webhook server is running (PID: $(cat $PID_FILE))"
      curl -s http://localhost:8080/ | python3 -m json.tool 2>/dev/null || echo "Health check failed"
    else
      echo "Webhook server is not running"
    fi
    ;;
    
  restart)
    $0 stop
    sleep 1
    $0 start
    ;;
    
  *)
    echo "Usage: $0 {start|stop|status|restart}"
    exit 1
    ;;
esac
