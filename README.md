# 九重天试 — AI vs 人类博弈游戏

> 九关递增难度，每关不同博弈类型，与 AI 天神斗智斗勇

## 游戏概览

| 关卡 | 名称 | 博弈类型 | 天神 | 难度 | 预估胜率 |
|------|------|----------|------|------|----------|
| 1 | 谎言之门 | 信号博弈 | 谛听 | ⭐⭐ | ~70% |
| 2 | 囚徒之局 | 重复囚徒困境 | 裁决 | ⭐⭐ | ~55% |
| 3 | 分金博弈 | 最后通牒 | 分配 | ⭐⭐⭐ | ~50% |
| 4 | 谈判桌 | 多议题谈判 | 契约 | ⭐⭐⭐ | ~45% |
| 5 | 信任之桥 | 信任博弈+干扰 | 信守 | ⭐⭐⭐ | ~40% |
| 6 | 海盗分金 | 多人投票博弈 | 分配 | ⭐⭐⭐⭐ | ~35% |
| 7 | 谎言猎手 | 信息战/推理 | 真言 | ⭐⭐⭐⭐ | ~30% |
| 8 | 镜中对决 | 石头剪刀布+AI学习 | 镜像 | ⭐⭐⭐⭐⭐ | ~25% |
| 9 | 天神之局 | 三关综合 | 本尊 | ⭐⭐⭐⭐⭐ | ~15% |

## 项目状态

- [x] 架构设计
- [x] 后端框架搭建
- [x] 9 关游戏逻辑实现
- [x] AI Prompt 工程
- [ ] 前端小程序
- [ ] 上线部署

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

### 2. 创建虚拟环境

```bash
uv venv .venv --python 3.12
uv pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入：
# QWEN_API_KEY=你的千问API Key
```

### 4. 运行服务

```bash
.venv\Scripts\python -m uvicorn app.main:app --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /health | 健康检查 |
| GET | /api/game/levels | 列出所有关卡 |
| POST | /api/game/start | 开始游戏 |
| POST | /api/game/message | 发送消息 |
| GET | /api/game/status/{player_id} | 查询状态 |
| WS | /api/chat/ws | WebSocket 实时对话 |

### 示例：开始第一关

```bash
curl -X POST http://localhost:8000/api/game/start \
  -H "Content-Type: application/json" \
  -d '{"player_id":"player1","level_id":1}'
```

### 示例：发送消息

```bash
curl -X POST http://localhost:8000/api/game/message \
  -H "Content-Type: application/json" \
  -d '{"player_id":"player1","content":"甲门"}'
```

## 项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 全局配置
│   ├── api/                 # API 路由层
│   │   ├── auth.py         # 微信登录
│   │   ├── game.py         # 游戏控制
│   │   ├── chat.py         # WebSocket
│   │   └── leaderboard.py  # 排行榜
│   ├── services/           # 业务逻辑层
│   │   ├── game_service.py
│   │   └── chat_service.py
│   ├── core/               # 核心引擎
│   │   ├── session_manager.py  # 多会话管理
│   │   ├── level_manager.py    # 关卡注册
│   │   └── ai_controller.py    # AI 控制
│   ├── levels/             # 关卡实现
│   │   ├── base.py        # 抽象基类
│   │   └── level_01~09.py # 各关逻辑
│   ├── prompts/            # Prompt 工程
│   │   └── base_prompt.py # 四层构建器
│   └── infra/              # 基础设施
│       ├── llm_adapter.py  # 千问适配器
│       └── database.py     # SQLite
└── tests/                  # 测试
```

## 设计文档

- [游戏设计文档](docs/game-design.md)
- [技术方案](docs/technical-design.md)
- [后端架构](docs/backend-architecture.md)
- [调研报告](docs/research.md)

## 开发日志

- **2026-04-03**: 完成 9 关游戏逻辑 + AI Prompts
- **2026-04-03**: 后端框架搭建 + API 测试通过

## License

MIT
