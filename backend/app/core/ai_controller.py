"""
AI Controller - Scene generation + judgment + strategic response
"""
import json
import random
from app.infra.llm_adapter import QwenAdapter
from app.core.session_manager import GameSession


MODEL_CONFIG = {
    range(1, 4):  ("qwen-turbo", 0.8, 600),
    range(4, 7):  ("qwen-plus",  0.6, 800),
    range(7, 10): ("qwen-plus",  0.5, 1000),
}


def _model(level_id: int):
    for rng, cfg in MODEL_CONFIG.items():
        if level_id in rng:
            return cfg
    return "qwen-plus", 0.6, 800


JUDGE_PROMPT = """你是一个严格、公正的游戏裁判。

当前关卡信息：
- 关卡ID: {level_id}
- 关卡名称: {level_name}
- 天神名: {deity_name}
- 游戏背景: {context}

玩家输入: "{player_input}"

你的选项:
{options_text}

请严格判断玩家输入属于哪个选项（精确匹配关键词），然后输出JSON：
{{"type": "win|lose|continue", "score_delta": 0~30, "option": "选项名", "text": "天神回应（2-3句，半文言神秘风格）"}}

规则：
- type=win: 玩家做出了正确/明智的选择
- type=lose: 玩家做出了错误/被惩罚的选择
- type=continue: 玩家需要更多信息，还不能判断胜负
- 每次得分不超过30分
- 天神说话要有角色感，不重复"""

SCENE_PROMPT = """你是九重天试的天神，为当前关卡生成一个独特的游戏场景。

关卡信息：
- 关卡ID: {level_id}
- 关卡名称: {level_name}
- 天神名: {deity_name}
- 难度: {difficulty}
- 游戏类型: {game_type}

规则说明：{rules_hint}

回合历史（最近的对话）：
{history}

请生成一个新的游戏场景，输出JSON：
{{
  "intro": "开场白（天神说1-2句，神秘有气势）",
  "text": "场景描述（描述当前情境，50字左右，有画面感）",
  "options": [
    {{"key": "A", "text": "选项A的描述"}},
    {{"key": "B", "text": "选项B的描述"}},
    {{"key": "C", "text": "选项C的描述（可选）"}}
  ],
  "hint": "给玩家的提示（1句，不透露答案）",
  "win_condition": "过关条件（用2-3句话告诉玩家：怎样才算通过本关，要具体明确）",
  "difficulty_hint": "难度提示"
}}

要求：
- 每次生成的场景都不同（用随机性元素）
- options 包含 2-3 个合理选项，有陷阱选项
- 场景要有故事感，不只是干巴巴的选择题
- text 用第二人称"你"描述"""

OPENING_PROMPT = """你是九重天试的天神，即将开始第一关。

你是{deity_name}，掌管{level_name}。

请用你的威严和神秘感，说一段开场白（3-4句），告诉挑战者：
1. 这是第几关
2. 你将如何考验他
3. 提示他可以用自然语言自由输入你的选择

然后输出一段场景描述，格式如下（JSON）：
{{"intro": "开场白", "text": "场景描述", "options": [{{"key":"A","text":"选项A"}},{{"key":"B","text":"选项B"}}], "hint": "提示"}}

风格：半文言，半白话，有气势，有神秘感。"""


class AIController:
    def __init__(self):
        self.llm = QwenAdapter()

    async def _call(self, messages: list, level_id: int) -> str:
        model, temp, max_tok = _model(level_id)
        return await self.llm.chat(messages, model=model,
                                   temperature=temp, max_tokens=max_tok)

    def _extract_json(self, text: str) -> dict | None:
        """从 LLM 输出中提取 JSON"""
        for start in ["{", "【{"]:
            idx = text.find(start)
            if idx >= 0:
                text = text[idx:]
                depth = 0
                for i, c in enumerate(text):
                    if c == "{": depth += 1
                    elif c == "}":
                        depth -= 1
                        if depth == 0:
                            try:
                                return json.loads(text[:i+1])
                            except json.JSONDecodeError:
                                pass
        return None

    def _history_text(self, session: GameSession) -> str:
        msgs = session.messages[-6:] if session.messages else []
        if not msgs:
            return "（这是第一回合）"
        return "\n".join(
            f"[{'你' if m.get('role')=='player' else '天神'}]: {m.get('content','')[:80]}"
            for m in msgs
        )

    async def generate_scene(
        self, session: GameSession, level, player_input: str = ""
    ) -> dict:
        """Generate a new game scene for current level."""
        hist = self._history_text(session)
        template = SCENE_PROMPT.format(
            level_id=level.level_id,
            level_name=level.name,
            deity_name=level.deity_name,
            difficulty=level.difficulty,
            game_type=level.description[:30],
            rules_hint=level.rules_hint,
            history=hist,
        )
        messages = [
            {"role": "system", "content": self._system_prompt(level)},
            {"role": "user", "content": template},
        ]
        raw = await self._call(messages, session.level_id)
        data = self._extract_json(raw)
        if data:
            return data

        # Fallback: structured scene
        return self._fallback_scene(level, session)

    def _system_prompt(self, level) -> str:
        return f"""你是{level.deity_name}，掌管{level.name}。

你威严、神秘、充满智慧。说话用半文言风格，简短有力。

你主持一场博弈游戏。你会：
1. 描述当前场景
2. 提供多个选项（用字母A/B/C标识）
3. 根据玩家的自然语言输入判断他选择了哪个选项
4. 给出奖惩结果

重要：你必须从玩家的文字中理解他的意图，而不是机械匹配。"""

    async def judge_input(
        self, session: GameSession, level, player_input: str,
        current_scene: dict
    ) -> dict:
        """Judge player's input against current scene options."""
        options = current_scene.get("options", [])
        options_text = "\n".join(
            f"- [{o.get('key','?')}] {o.get('text','')}"
            for o in options
        ) or "无预设选项，自由输入"

        # If no structured options, use free-form judgment
        if not options:
            return await self._free_judge(session, level, player_input)

        template = JUDGE_PROMPT.format(
            level_id=level.level_id,
            level_name=level.name,
            deity_name=level.deity_name,
            context=current_scene.get("text", level.description),
            player_input=player_input,
            options_text=options_text,
        )
        messages = [
            {"role": "system", "content": self._system_prompt(level)},
            {"role": "user", "content": template},
        ]
        raw = await self._call(messages, session.level_id)
        data = self._extract_json(raw)
        if data:
            return data

        # Fallback: use simple keyword matching
        return self._fallback_judge(options, player_input)

    async def _free_judge(
        self, session: GameSession, level, player_input: str
    ) -> dict:
        """Free-form judgment when no structured options exist."""
        # Very simple fallback - don't overuse AI calls
        p = player_input.lower()
        # Detect positive/negative intent
        good = any(w in p for w in ["好", "是", "对", "选", "接受", "同意", "合作", "建", "给", "愿意"])
        bad = any(w in p for w in ["不", "否", "拒绝", "背叛", "不要", "退出"])
        if good and not bad:
            return {"type": "win", "score_delta": 20,
                    "text": f"善，天神微微颔首。{player_input[:10]}…可。"
                    if len(player_input) > 3 else "善。"}
        elif bad:
            return {"type": "continue", "score_delta": 0,
                    "text": "天神不语，示意你继续。"}
        else:
            return {"type": "continue", "score_delta": 0,
                    "text": "天神静静看着你，等待你的决定。"}

    def _fallback_scene(self, level, session) -> dict:
        """Fallback scene when LLM JSON parsing fails."""
        scenes = {
            1: {
                "intro": "挑战者，你来到第一道试炼。",
                "text": "你面前有两条路：左边金光闪闪，右边幽暗深邃。两条路都可能是通往宝藏的正道——或者陷阱。",
                "options": [
                    {"key": "A", "text": "走左边的金光之路"},
                    {"key": "B", "text": "走右边的幽暗之路"},
                    {"key": "C", "text": "先观察周围环境"},
                ],
                "hint": "金光未必是真道，幽暗未必是绝路。",
            },
            2: {
                "intro": "囚徒之局开启。你与天神将进行一场心理博弈。",
                "text": "你面前有一枚宝物。你可以选择「分享」，也可以选择「独占」。天神同时在做出选择。你知道：只有双方都分享，才能各得3分…",
                "options": [
                    {"key": "A", "text": "分享宝物"},
                    {"key": "B", "text": "独占宝物"},
                ],
                "hint": "天神是聪明的，但你也不是没有机会。",
            },
            3: {
                "intro": "分金博弈开始。",
                "text": "你有100枚金币。你需要向天神提出分配方案。如果天神觉得不公平，你们都将空手而归。",
                "options": [
                    {"key": "A", "text": "提出平等分配：各50枚"},
                    {"key": "B", "text": "给自己70枚，给天神30枚"},
                    {"key": "C", "text": "给天神大部分，自己只拿少量"},
                ],
                "hint": "过于贪婪会被拒绝，过于慷慨会损失太多。",
            },
        }
        default = {
            "intro": f"第{level.level_id}关：{level.name}",
            "text": f"{level.deity_name}向你展示了一道选择。",
            "options": [
                {"key": "A", "text": "选择A"},
                {"key": "B", "text": "选择B"},
                {"key": "C", "text": "谨慎地观察"},
            ],
            "hint": level.rules_hint,
        }
        return scenes.get(level.level_id, default)

    def _fallback_judge(self, options: list, player_input: str) -> dict:
        """Fallback judgment using simple keyword matching."""
        p = player_input.lower()
        for opt in options:
            key = opt.get("key", "").upper()
            text = opt.get("text", "").lower()
            # Check if player mentions option key
            if key in p or any(w in p for w in text[:6]):
                return {
                    "type": random.choices(
                        ["win", "lose", "continue"],
                        weights=[0.5, 0.2, 0.3]
                    )[0],
                    "score_delta": random.randint(10, 25),
                    "option": key,
                    "text": f"天神回应：{opt.get('text', '你的选择已记录。')}",
                }
        return {
            "type": "continue",
            "score_delta": 0,
            "text": "天神静静等待你做出选择…",
        }
