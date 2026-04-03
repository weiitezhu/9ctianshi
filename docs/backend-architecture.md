# 九重天试 — 后端服务架构设计（MVP 版）

> 基于微信小程序 + 千问系列大模型
> 日期：2026-04-03 | 版本：v0.2

---

## 一、整体分层架构

前端（微信小程序）→ API网关 → 服务层（认证/游戏/对话/排行）→ 基础设施层（LLM/数据库/缓存）

---

## 二、后端项目结构

`
backend/
├── app/
│   ├── main.py                  # FastAPI 入口
│   ├── config.py                # 全局配置
│   ├── api/                     # API 层（薄层）
│   ├── services/                # 业务逻辑层
│   ├── core/                    # 核心引擎层
│   │   ├── game_engine.py       # 游戏状态机
│   │   ├── level_manager.py     # 关卡管理
│   │   ├── ai_controller.py     # AI 控制
│   │   └── session_manager.py   # 多会话管理
│   ├── levels/                  # 关卡实现
│   ├── prompts/                 # Prompt 工程
│   ├── infra/                   # 基础设施
│   │   ├── llm_adapter.py       # 千问适配器
│   │   ├── database.py          # SQLite
│   │   └── wechat.py            # 微信登录
│   └── models/                  # 数据模型
├── prompts/                     # Prompt 文件
├── tests/
└── requirements.txt
`

---

## 三、多会话管理设计

每个玩家可同时有多个游戏会话（不同关卡），会话状态：
- ACTIVE（进行中）
- PAUSED（暂停，可恢复）
- COMPLETED（已完成）
- EXPIRED（超时失效）

会话超时时间：30分钟

---

## 四、千问模型适配

支持的模型：
- qwen-turbo: 快速便宜，第1-2关
- qwen-plus: 均衡，第3关
- qwen-max: 最强，第4-9关

API 地址：https://dashscope.aliyuncs.com/compatible-mode/v1

---

## 五、Prompt 分层架构

四层拼接：
1. 基础人格（所有关卡共享）
2. 关卡规则（当前关卡专属）
3. 动态状态（轮次、剩余操作等）
4. 安全护栏（防 Prompt Injection）

---

## 六、核心 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/login | 微信登录 |
| POST | /api/game/start | 开始某关 |
| WS | /api/chat/ws | 实时对话 |

---

## 七、MVP 范围

包含：前3关 + 微信小程序基础版 + FastAPI后端 + 千问API
不包含：第4-9关、支付、复杂UI

---

## 八、成本估算

平均每局 ¥0.005
100玩家每天5局 = 月成本 ¥75
