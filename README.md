# Muon — Sleep & Focus Sounds

一个极简美学的沉浸式音景混合器 iOS App。

## 功能

- 🎵 18个精选高品质音效（自然、室内、婴儿安抚）
- 🎛️ 同时混合最多4个音效，独立音量控制
- ⏱️ 睡眠定时器，渐弱停止
- 👶 婴儿安抚模式（子宫心跳、血流等科学验证音效）
- 💾 保存收藏混音组合
- 📴 完全离线可用
- 💰 一次性买断 $3.99，无订阅

## 技术栈

- Swift / SwiftUI
- AVAudioEngine（多音轨混合）
- StoreKit 2（IAP）
- 目标：iOS 16.0+

## 项目结构

```
Muon/
├── MuonApp.swift           # App入口
├── Models/                 # 数据模型
├── Audio/                  # 音频引擎
├── Store/                  # IAP管理
├── Views/                  # SwiftUI视图
│   └── Components/         # 可复用组件
└── Resources/Sounds/       # 音频文件 (.m4a)
```

## 音效来源

- 全部18个音效由算法生成（Weaveon 自有版权）
- Pixabay.com（Pixabay Content License — 免费商用，用于未来更新）
- 详细归属信息见 [CREDITS.md](CREDITS.md)

## 构建

1. 用 Xcode 15+ 打开项目
2. 将音频文件(.m4a)放入 `Resources/Sounds/`
3. 在 App Store Connect 创建非消耗型IAP: `com.weaveon.muon.premium`
4. 运行

## License

Copyright © 2026 Weaveon. All rights reserved.
