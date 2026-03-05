#!/bin/bash
# Android 模拟器全自动安装脚本 - 无需交互
# 用于开盘啦 APP 抓包

set -e

echo "=== Android 模拟器全自动安装 ==="

# 配置
ANDROID_HOME="$HOME/android-sdk"
CMDLINE_TOOLS_URL="https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip"

# 1. 创建目录
mkdir -p "$ANDROID_HOME"
cd "$ANDROID_HOME"

# 2. 下载命令行工具（如果不存在）
if [ ! -d "cmdline-tools/latest" ]; then
    echo "📥 下载 Android 命令行工具..."
    wget -q --show-progress "$CMDLINE_TOOLS_URL" -O cmdline-tools.zip
    unzip -q cmdline-tools.zip
    mkdir -p cmdline-tools/latest
    mv cmdline-tools/* cmdline-tools/latest/ 2>/dev/null || true
    rm -f cmdline-tools.zip
fi

# 3. 设置环境变量
export ANDROID_HOME
export PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator"

# 4. 自动接受所有 license（关键：无需手动点击 Yes）
echo "📋 自动接受 licenses..."
yes | sdkmanager --licenses > /dev/null 2>&1 || true

# 5. 安装必要组件
echo "📦 安装必要组件..."
sdkmanager --install "platform-tools" "platforms;android-30" "emulator" "system-images;android-30;google_apis;x86_64" > /dev/null 2>&1

# 6. 创建模拟器（自动覆盖，无需确认）
echo "📱 创建 Android 模拟器..."
avdmanager create avd \
    -n "kaipanla_avd" \
    -k "system-images;android-30;google_apis;x86_64" \
    -d "pixel" \
    --force \
    --sdcard 512M

# 7. 配置模拟器（无窗口模式、无音频）
cat > "$ANDROID_HOME/.android/avd/kaipanla_avd.avd/config.ini" << 'EOF'
PlayStore.enabled=false
abi.type=x86_64
avd.ini.encoding=UTF-8
avd.name=kaipanla_avd
disk.dataPartition.size=2G
fastboot.forceColdBoot=no
hw.accelerometer=yes
hw.arc=false
hw.audioInput=yes
hw.battery=yes
hw.camera.back=virtualscene
hw.camera.front=emulated
hw.cpu.arch=x86_64
hw.cpu.ncore=2
hw.dPad=no
hw.device.hash2=MD5:3db3250dab5d0d93b2934f979dc11f33
hw.device.manufacturer=Google
hw.device.name=pixel
hw.gps=yes
hw.gpu.enabled=no
hw.gpu.mode=off
hw.initialOrientation=Portrait
hw.keyboard=yes
hw.lcd.density=420
hw.lcd.height=1920
hw.lcd.width=1080
hw.mainKeys=no
hw.ramSize=1536
hw.sdCard=yes
hw.sensors.orientation=yes
hw.sensors.proximity=yes
hw.trackBall=no
runtime.network.latency=none
runtime.network.speed=full
sdcard.size=512M
showDeviceFrame=no
skin.dynamic=yes
skin.name=1080x1920
skin.path=_no_skin
tag.display=Google APIs
tag.id=google_apis
target=android-30
EOF

echo ""
echo "✅ Android 模拟器安装完成！"
echo ""
echo "📍 安装路径: $ANDROID_HOME"
echo "📱 模拟器名称: kaipanla_avd"
echo ""
echo "🚀 启动命令:"
echo "   export ANDROID_HOME=$ANDROID_HOME"
echo "   export PATH=\"\$PATH:\$ANDROID_HOME/emulator:\$ANDROID_HOME/platform-tools\""
echo "   emulator -avd kaipanla_avd -no-window -no-audio -gpu off &"
echo ""
echo "📲 安装开盘啦 APK:"
echo "   adb install kaipanla.apk"
echo ""
