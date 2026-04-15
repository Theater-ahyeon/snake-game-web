# Snake Game Pro - Kinetic Luminescence Edition

<p align="center">
    <img src="https://img.shields.io/badge/HTML5-Canvas-orange?style=for-the-badge" alt="HTML5">
    <img src="https://img.shields.io/badge/JavaScript-ES6+-yellow?style=for-the-badge" alt="JavaScript">
    <img src="https://img.shields.io/badge/Python-Flask-blue?style=for-the-badge" alt="Flask">
    <img src="https://img.shields.io/badge/Electron-Desktop-blue?style=for-the-badge" alt="Electron">
    <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

<p align="center">
    🎮 一款基于"Kinetic Luminescence"设计系统打造的超级精美贪吃蛇游戏 - 霓虹发光效果、玻璃态界面、8种皮肤系统、实时排行榜！
</p>

---

## ✨ 功能特性

### 🎨 Kinetic Luminescence 设计系统
- 🌟 霓虹绿主色调 (#8eff71) + 青色辅助 (#00eefc) + 粉红强调 (#ff59e3)
- ✨ 玻璃态界面 (Glassmorphism) + backdrop-filter 模糊效果
- 💫 Space Grotesk + Manrope 字体配对
- 🔮 动态发光阴影、网格背景、呼吸动画
- 🎨 8种蛇皮肤（霓虹绿、赛博粉、海洋蓝、夕阳橙、黄金、星际紫、烈焰红、彩虹）

### 🎮 游戏模式
- **经典** - 经典模式，无障碍物
- **障碍** - 随机生成障碍物
- **幽灵** - 蛇移动后留下渐消失的轨迹
- **无尽** - 无限生存挑战模式

### 📊 关卡系统
- 8个精心设计的关卡
- 逐步解锁机制（根据累计分数）
- 不同的地图大小、障碍物数量和速度

### 💊 道具系统
- ⚡ 加速道具 - 短时间内移动更快
- 🛡️ 护盾道具 - 免疫一次碰撞
- 2️⃣ 双倍得分道具 - 短时间内得分翻倍

### 🏆 成就系统
- 14个成就徽章
- 实时弹窗通知
- 进度持久化

### 👥 社交功能
- 好友系统
- 战绩分享（生成图片）
- 观战模式

### 🏆 排行榜
- 全球排行榜
- 分模式排名（经典/障碍/幽灵/无尽）
- **实时WebSocket更新**

### 🌍 国际化
- 中文/English 语言切换

### 💻 桌面应用
- Electron 打包的原生 Windows 应用
- 便携版无需安装，双击即玩

---

## 🚀 快速开始

### 桌面版（推荐）
下载 `SnakeGamePro-Portable.zip` 并解压，双击 `snake-game-pro.exe` 即可游戏！

### Web 版本
直接双击 `index.html` 文件在浏览器中打开即可游戏！

### 完整版（需要后端）

#### 1. 启动后端服务
```bash
cd backend
pip install -r requirements.txt
python app.py
```

后端服务将在 `http://localhost:5000` 启动。

#### 2. 打开前端
在浏览器中打开 `index.html`

---

## 🎮 操作说明

| 按键 | 功能 |
|------|------|
| W / ↑ | 向上移动 |
| S / ↓ | 向下移动 |
| A / ← | 向左移动 |
| D / → | 向右移动 |
| R | 重新开始 |
| P | 暂停 |

**移动端**: 点击屏幕上的虚拟方向按钮

---

## 🎨 设计系统：Kinetic Luminescence

"Kinetic Luminescence" 是一种将界面作为发光光源的设计理念。通过以下技术实现：

1. **无线条规则** - 使用背景色调变化定义区域，不用1px白色实线
2. **玻璃态叠层** - backdrop-filter: blur(16px) 创建磨砂玻璃效果
3. **渐变光晕** - 按钮使用 135° 渐变 (primary → primary-container) 模拟液态光
4. **霓虹阴影** - 使用主色 5-8% 透明度 + 40px 模糊代替传统阴影
5. **色调深度** - 通过堆叠不同级别的 surface 容器实现纵深感

详细设计规范请参考 `stitch_snake_game_pro_neon/` 目录。

---

## 📁 项目结构

```
snake_game_web/
├── index.html              # 前端主文件（完整功能）
├── SnakeGamePro-Portable.zip # Windows 便携版
├── stitch_snake_game_pro_neon/  # 设计方案
├── backend/
│   ├── app.py              # Flask 后端应用
│   ├── requirements.txt    # Python 依赖
│   └── README.md           # 后端说明
└── README.md               # 项目说明
```

---

## 🔓 皮肤系统

| 皮肤 | 名称 | 解锁条件 |
|------|------|----------|
| neon | 霓虹绿 | 默认解锁 |
| cyber | 赛博粉 | 默认解锁 |
| ocean | 海洋蓝 | 默认解锁 |
| sunset | 夕阳橙 | 默认解锁 |
| gold | 黄金 | 单局得分 ≥ 500 |
| purple | 星际紫 | 单局得分 ≥ 1000 |
| fire | 烈焰红 | 无尽模式 ≥ 1000 |
| rainbow | 彩虹 | 无尽模式 ≥ 5000 |

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 自由使用，开心游戏！

---

<p align="center">
    Made with ❤️ by Claude | Kinetic Luminescence Design System
</p>
