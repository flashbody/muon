#!/bin/bash
set -e

PROJECT_DIR="/Users/a39/Documents/AIProject/Weaveon/Muon"
SIMULATOR="iPhone 17"
BUNDLE_ID="com.weaveon.muon"

echo "=========================================="
echo "Muon - 编译并运行到模拟器"
echo "=========================================="

# 1. 生成 Xcode 项目
echo "[1/6] 生成 Xcode 项目..."
cd "$PROJECT_DIR"
xcodegen generate

# 2. 清理并编译
echo "[2/6] 清理并编译..."
xcodebuild -project Muon.xcodeproj -scheme Muon -destination "platform=iOS Simulator,name=$SIMULATOR" clean build | tail -5

# 3. 查找编译好的 App 路径
APP_PATH=$(find ~/Library/Developer/Xcode/DerivedData/Muon-* -name "Muon.app" -type d 2>/dev/null | head -1)
if [ -z "$APP_PATH" ]; then
    echo "错误：找不到编译好的 Muon.app"
    exit 1
fi
echo "  App 路径: $APP_PATH"

# 4. 卸载旧版本
echo "[3/6] 卸载旧版本..."
xcrun simctl uninstall "$SIMULATOR" "$BUNDLE_ID" 2>/dev/null || true

# 5. 安装新版本
echo "[4/6] 安装新版本..."
xcrun simctl install "$SIMULATOR" "$APP_PATH"

# 6. 启动 App
echo "[5/6] 启动 App..."
xcrun simctl launch "$SIMULATOR" "$BUNDLE_ID"

# 7. 等待启动动画完成，然后截图
echo "[6/6] 等待 5 秒后截图..."
sleep 5
SCREENSHOT_PATH="$PROJECT_DIR/muon_screenshot_$(date +%Y%m%d_%H%M%S).png"
xcrun simctl io "$SIMULATOR" screenshot "$SCREENSHOT_PATH"

echo ""
echo "=========================================="
echo "完成！"
echo "截图已保存到: $SCREENSHOT_PATH"
echo "请打开截图，查看："
echo "  1. 是否全屏（还是四周有黑边）？"
echo "  2. 左上角红色文字显示什么数字？"
echo "=========================================="
