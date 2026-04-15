# Snake Game Pro - 贪吃蛇

<p align="center">
    <img src="https://img.shields.io/badge/HTML5-Canvas-orange?style=for-the-badge" alt="HTML5">
    <img src="https://img.shields.io/badge/JavaScript-ES6+-yellow?style=for-the-badge" alt="JavaScript">
    <img src="https://img.shields.io/badge/Python-Flask-blue?style=for-the-badge" alt="Flask">
    <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

<p align="center">
    🎮 一款使用纯 HTML5 Canvas 开发的超级精美贪吃蛇游戏 - 现在支持完整前后端！
</p>

<p align="center">
    <img src="https://img.shields.io/badge/Platform-Windows-blue?style=flat-square" alt="Platform">
    <img src="https://img.shields.io/badge/Platform-macOS-blue?style=flat-square" alt="Platform">
    <img src="https://img.shields.io/badge/Platform-Linux-blue?style=flat-square" alt="Platform">
    <img src="https://img.shields.io/badge/Platform-Mobile-blue?style=flat-square" alt="Platform">
</p>

---

## ✨ 功能特性

### 🎨 视觉效果
- 🌟 霓虹发光效果的蛇身
- ✨ 粒子爆炸特效
- 💫 食物呼吸动画
- 🔮 渐变背景
- 🎨 动态边框光效
- ⌨️ 按键反馈动画
- 🌌 星空背景

### 🎮 游戏模式
- **经典** - 经典模式，无障碍物
- **障碍** - 随机生成障碍物
- **幽灵** - 蛇移动后留下渐消失的轨迹
- **无尽** - 无限生存挑战模式

### 📊 关卡系统
- 8个精心设计的关卡
- 逐步解锁机制（根据累计分数）
- 不同的地图大小、障碍物数量和速度

### 💾 存档系统
- 游戏进度保存/读取（需登录）
- 断点续玩
- 自动存档支持

### 👤 用户系统
- 用户注册/登录
- 个人资料页面
- 游戏统计数据

### 🏆 排行榜
- 全球排行榜
- 分模式排名（经典/障碍/幽灵/无尽）
- 无尽模式记录

---

## 🚀 快速开始

### Web 版本（无需后端）

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

在浏览器中打开 `index.html`，或使用本地服务器：

```bash
python -m http.server 8000
# 访问 http://localhost:8000
```

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

## 📁 项目结构

```
snake_game_web/
├── index.html          # 前端主文件
├── backend/
│   ├── app.py          # Flask 后端应用
│   ├── requirements.txt # Python 依赖
│   └── README.md       # 后端说明
└── README.md           # 项目说明
```

---

## 🎨 技术栈

### 前端
- **HTML5 Canvas** - 游戏渲染
- **CSS3** - 精美动画效果
- **Vanilla JavaScript** - 游戏逻辑
- **LocalStorage** - 本地数据持久化

### 后端
- **Python Flask** - Web 框架
- **SQLite** - 数据库
- **Flask-CORS** - 跨域支持

---

## 🎯 游戏规则

1. 使用 **WASD** 或 **方向键** 控制蛇的移动方向
2. 吃食物获得 **+10 分**，蛇身长度 **+1**
3. 撞到墙壁、障碍物或自己的身体 **游戏结束**
4. 尽量获得更高的分数吧！

---

## 🏆 排行榜说明

| 模式 | 说明 |
|------|------|
| 全部 | 所有玩家的综合排名 |
| 经典 | 经典模式排名 |
| 障碍 | 障碍物模式排名 |
| 幽灵 | 幽灵模式排名 |
| 无尽 | 无尽模式排名 |

---

## 🔓 关卡解锁

| 关卡 | 名称 | 解锁条件 |
|------|------|----------|
| 1 | 初出茅庐 | 默认解锁 |
| 2 | 小试牛刀 | 总分 ≥ 100 |
| 3 | 稳步提升 | 总分 ≥ 300 |
| 4 | 身手不凡 | 总分 ≥ 600 |
| 5 | 炉火纯青 | 总分 ≥ 1000 |
| 6 | 出神入化 | 总分 ≥ 1500 |
| 7 | 登峰造极 | 总分 ≥ 2500 |
| 8 | 独孤求败 | 总分 ≥ 4000 |

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 自由使用，开心游戏！

---

<p align="center">
    Made with ❤️ by Claude
</p>
