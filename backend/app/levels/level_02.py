"""Level 2: Prisoner's Dilemma - Repeated 5 rounds"""
import random
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession, SessionStatus
from app.core.level_manager import level_manager

# Payoff: (player, ai)
PAYOFFS = {
    ("cooperate", "cooperate"): (3, 3),
    ("cooperate", "betray"):    (0, 5),
    ("betray", "cooperate"):    (5, 0),
    ("betray", "betray"):       (1, 1),
}


class Level02(BaseLevel):
    level_id = 2
    name = "囚徒之局"
    description = "你和天神同时选择合作或背叛，连续5轮。积分高者胜。天神会学习你的策略。"
    difficulty = 0.30
    rules_hint = "每轮同时选择合作或背叛。5轮后积分高者通过。天神以眼还眼，但偶尔会出奇招。"
    deity_name = "裁决"
    win_rate_estimate = "~55%"

    def __init__(self):
        level_manager.register(2, self)

    async def on_start(self, session: GameSession) -> None:
        session.game_state = {
            "round": 0, "max_rounds": 5,
            "player_total": 0, "ai_total": 0,
            "history": [],
        }
        session.max_rounds = 5
        session.moves_left = 5
        session.score = 0.0

    def _parse(self, text: str) -> str | None:
        t = text.strip()
        if any(k in t for k in ["合作", "配合"]):
            return "cooperate"
        if any(k in t for k in ["背叛", "出卖"]):
            return "betray"
        return None

    def _ai_choose(self, gs: dict) -> str:
        h = gs.get("history", [])
        if not h:
            return random.choices(["cooperate", "betray"], weights=[0.6, 0.4])[0]
        last = h[-1]["player"]
        if random.random() < 0.8:
            return last  # tit-for-tat
        return random.choice(["cooperate", "betray"])

    async def on_message(self, session: GameSession, user_input: str) -> LevelResponse:
        gs = session.game_state
        choice = self._parse(user_input)
        if not choice:
            return LevelResponse(ai_text="请明确选择：合作，还是背叛？")

        gs["round"] += 1
        session.moves_left = gs["max_rounds"] - gs["round"]

        ai = self._ai_choose(gs)
        pp, ap = PAYOFFS[(choice, ai)]
        gs["player_total"] += pp
        gs["ai_total"] += ap
        gs["history"].append({"round": gs["round"], "player": choice, "ai": ai})

        cn = {"cooperate": "合作", "betray": "背叛"}
        text = f"第{gs['round']}轮：你「{cn[choice]}」，天神「{cn[ai]}」。你+{pp} 天神+{ap}（总分 你{gs['player_total']}:{gs['ai_total']}天神）"

        if gs["round"] >= gs["max_rounds"]:
            session.status = SessionStatus.COMPLETED
            won = gs["player_total"] > gs["ai_total"]
            tie = gs["player_total"] == gs["ai_total"]
            if tie:
                session.score = 50.0
                r = "平局"
                code = "tie"
            elif won:
                session.score = 100.0
                r = "你赢了！"
                code = "won"
            else:
                session.score = 0.0
                r = "天神赢了。"
                code = "lost"
            text += f"\n最终结果：{r}"
            return LevelResponse(
                ai_text=text,
                game_event={"type": "game_over", "result": code, "score": session.score,
                            "reason": r, "final_score": f"{gs['player_total']}:{gs['ai_total']}"},
                is_action=True,
            )

        return LevelResponse(
            ai_text=text + f"\n还剩{session.moves_left}轮。",
            game_event={"type": "round_end", "round": gs["round"]},
            is_action=True,
        )

    async def judge(self, session: GameSession) -> dict | None:
        return None

    def get_default_strategy(self) -> dict:
        return {"behavior": "tit_for_tat_with_noise", "initial_coop_prob": 0.6}


Level02()
