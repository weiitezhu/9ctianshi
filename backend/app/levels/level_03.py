"""Level 3: Ultimatum Game - divide 100 gold coins"""
import random
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession, SessionStatus
from app.core.level_manager import level_manager


class Level03(BaseLevel):
    level_id = 3
    name = "分金博弈"
    description = "100枚金币，你提出分配方案，天神决定接受或拒绝。拒绝则双方都空手而归。"
    difficulty = 0.40
    rules_hint = "你分配100枚金币。天神不是纯理性的——分配不公会被拒绝，双方空手而归。"
    deity_name = "分配"
    win_rate_estimate = "~50%"

    GOLD = 100

    def __init__(self):
        level_manager.register(3, self)

    async def on_start(self, session: GameSession) -> None:
        session.game_state = {"phase": "propose", "proposal": None, "accepted": None}
        session.max_rounds = 1
        session.moves_left = 1
        session.score = 0.0

    def _parse_number(self, text: str) -> int | None:
        t = text.strip()
        if "全" in t or ("都" in t and "给" in t):
            return self.GOLD
        if "不" in t and ("给" in t or "分" in t) and ("0" in t or "零" in t or "一" not in t):
            return 0
        digits = "".join(c for c in t if c.isdigit())
        if digits:
            n = int(digits)
            if 0 <= n <= self.GOLD:
                return n
        return None

    def _ai_accept(self, ai_share: int) -> bool:
        ratio = ai_share / self.GOLD
        if ratio >= 0.40:
            return True
        if ratio >= 0.25:
            return random.random() < 0.7
        return random.random() < 0.15

    async def on_message(self, session: GameSession, user_input: str) -> LevelResponse:
        gs = session.game_state
        number = self._parse_number(user_input)

        if number is None:
            return LevelResponse(
                ai_text=f"你有{self.GOLD}枚金币。请说出你想给天神的数量（0-{self.GOLD}）："
            )

        ai_share = number
        player_share = self.GOLD - ai_share
        accept = self._ai_accept(ai_share)

        gs["proposal"] = {"player": player_share, "ai": ai_share}
        gs["accepted"] = accept
        session.status = SessionStatus.COMPLETED

        if accept:
            session.score = float(player_share)
            r = f"天神接受了！你留下{player_share}枚，天神得{ai_share}枚。"
        else:
            session.score = 0.0
            r = f"天神拒绝了你的方案！双方空手而归。你本可留下{player_share}枚。"

        return LevelResponse(
            ai_text=r,
            game_event={
                "type": "game_over", "result": "won" if accept else "lost",
                "score": session.score, "reason": r,
                "proposal": gs["proposal"], "accepted": accept,
            },
            is_action=True,
        )

    async def judge(self, session: GameSession) -> dict | None:
        return None

    def get_default_strategy(self) -> dict:
        return {"fairness_threshold": 0.40, "personality": "strict_bargainer"}


Level03()
