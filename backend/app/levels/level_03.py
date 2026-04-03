"""Level 3: Ultimatum Game - Fairness bargaining"""
import random
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession, SessionStatus
from app.core.level_manager import level_manager


class Level03(BaseLevel):
    """Player proposes split of 100 gold. Deity accepts or rejects (reject = both get 0)."""

    level_id = 3
    name = "The Ultimatum"
    description = "You have 100 gold. Propose a split. The deity accepts or rejects. If rejected, both get nothing."
    difficulty = 0.40
    rules_hint = "Offer too little and the deity rejects out of spite. Offer enough and it accepts."
    deity_name = "The Divider"
    win_rate_estimate = "~50%"
    GOLD = 100

    def __init__(self):
        level_manager.register(3, self)

    async def on_start(self, session: GameSession) -> None:
        session.game_state = {"phase": "propose"}
        session.max_rounds = 1
        session.score = 0.0

    def _extract_number(self, text: str) -> int | None:
        digits = "".join(c for c in text if c.isdigit())
        if digits:
            n = int(digits)
            if 0 <= n <= self.GOLD: return n
        if "all" in text.lower() or "everything" in text.lower(): return self.GOLD
        return None

    async def on_message(self, session: GameSession, user_input: str) -> LevelResponse:
        n = self._extract_number(user_input)
        if n is None:
            return LevelResponse(ai_text=f"You have {self.GOLD} gold. How much do you offer the deity? (0-{self.GOLD})", is_action=False)

        player_share = n
        ai_share = self.GOLD - player_share
        accept = self._ai_decide(ai_share)
        session.status = SessionStatus.COMPLETED

        if accept:
            session.score = float(player_share)
            reason = f"Accepted! You keep {player_share}, deity gets {ai_share}."
            rc = "won"
        else:
            session.score = 0.0
            reason = "Rejected! Both get nothing."
            rc = "lost"

        return LevelResponse(ai_text=reason,
            game_event={"type": "game_over", "result": rc, "score": session.score,
                       "reason": reason, "proposal": {"player": player_share, "ai": ai_share},
                       "accepted": accept}, is_action=True)

    def _ai_decide(self, ai_share: int) -> bool:
        r = ai_share / self.GOLD
        if r >= 0.40: return random.random() < 0.95
        if r >= 0.25: return random.random() < 0.65
        if r >= 0.10: return random.random() < 0.15
        return random.random() < 0.02

    async def judge(self, session): return None
    def get_default_strategy(self): return {"fairness_threshold": 0.40}

Level03()
