# 九重天试 — AI vs 人类博弈游戏

> 九关递增难度，每关不同博弈类型，与 AI 天神斗智斗勇

## 项目状态

- [x] 架构设计
- [x] 后端框架搭建
- [ ] 第一关实现
- [ ] MVP 完成
- [ ] 发布

## 技术栈

- **后端**：Python 3.11 + FastAPI
- **AI**：千问系列大模型（DashScope API）
- **数据库**：SQLite（MVP）
- **前端**：微信小程序（规划中）

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/weiitezhu/9ctianshi.git
cd 9ctianshi/backend
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入以下内容：
# QWEN_API_KEY=你的千问API Key
# WECHAT_APP_ID=你的微信小程序AppID
# WECHAT_APP_SECRET=你的微信小程序AppSecret
```

### 4. 运行服务

```bash
uvicorn app.main:app --reload --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档

### 5. 运行测试

```bash
python -m pytest tests/ -v
```

## 项目结构

```
backend/
├── app/
│   ├── api/           # API 路由层
│   ├── services/      # 业务逻辑层
│   ├── core/          # 核心引擎
│   │   ├── game_engine.py      # 游戏状态机
│   │   ├── session_manager.py   # 多会话管理
│   │   ├── level_manager.py    # 关卡注册
│   │   ├── ai_controller.py    # AI 控制
│   │   └── judge.py            # 胜负判定
│   ├── levels/        # 关卡实现
│   ├── prompts/       # Prompt 工程
│   └── infra/         # 基础设施
│       ├── llm_adapter.py   # 千问适配器
│       └── database.py     # SQLite
├── prompts/           # Prompt 文件（与代码分离）
└── tests/             # 测试
```

## 九关总览

| 关卡 | 名称 | 博弈类型 | 难度 |
|------|------|----------|------|
| 1 | 谎言之门 | 信号博弈 | ⭐⭐ |
| 2 | 囚徒之局 | 囚徒困境 | ⭐⭐ |
| 3 | 分金博弈 | 最后通牒 | ⭐⭐⭐ |
| 4 | 谈判桌 | 谈判博弈 | ⭐⭐⭐ |
| 5 | 信任之桥 | 信任博弈 | ⭐⭐⭐ |
| 6 | 海盗分金 | 多人博弈 | ⭐⭐⭐⭐ |
| 7 | 谎言猎手 | 信息战 | ⭐⭐⭐⭐ |
| 8 | 镜中对决 | 元博弈 | ⭐⭐⭐⭐⭐ |
| 9 | 天神之局 | 综合博弈 | ⭐⭐⭐⭐⭐ |

## API 文档

启动服务后访问：http://localhost:8000/docs

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/login | 微信登录 |
| POST | /api/game/start | 开始游戏 |
| GET | /api/game/status/{player_id} | 获取游戏状态 |
| WS | /api/chat/ws | 实时对话 |

## 开发文档

- [游戏设计文档](docs/game-design.md)
- [技术方案](docs/technical-design.md)
- [后端架构](docs/backend-architecture.md)
- [调研报告](docs/research.md)
