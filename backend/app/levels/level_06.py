"""Level 6: Pirate's Gold - Multi-party strategic bargaining"""
import random, re
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession, SessionStatus
from app.core.level_manager import level_manager


class Level06(BaseLevel):
    """5 pirates, 100 gems. Player is #2. Must get 3/5 votes. Each pirate has personality."""

    level_id = 6
    name = "Pirate's Gold"
    description = "5 pirates divide 100 gems. You are #2. Need 3 votes to pass. Each pirate has different personality."
    difficulty = 0.65
    rules_hint = "Propose allocation for all 5 pirates (must sum to 100). Need 3 votes. Rational: 1+ gem. Greedy: 15+ gem. Angry: rejects if 0."
    deity_name = "The Captain"
    win_rate_estimate = "~35%"
    GEMS = 100
    NAMES = ["P1", "P2(You)", "P3", "P4", "P5"]
    # P1 already proposed (auto-rejected for narrative), player is P2
    TYPES = {
        "P1": {"type": "greedy", "min": 20},
        "P3": {"type": "rational", "min": 1},
        "P4": {"type": "greedy", "min": 15},
        "P5": {"type": "rational", "min": 1},
    }

    def __init__(self):
        level_manager.register(6, self)

    async def on_start(self, session: GameSession) -> None:
        session.game_state = {"phase": "propose", "attempts": 0}
        session.max_rounds = 3; session.score = 0.0

    def _parse(self, text: str) -> dict | None:
        alloc = {n: 0 for n in self.NAMES}
        for name in self.NAMES:
            clean = name.replace("(You)", "").replace("(", "").replace(")", "")
            pattern = rf'{clean}\D*(\d+)'
            m = re.search(pattern, text, re.IGNORECASE)
            if not m and len(clean) <= 2:
                pattern = rf'P{clean[-1]}\D*(\d+)'
                m = re.search(pattern, text, re.IGNORECASE)
            if m:
                alloc[name] = int(m.group(1))
        return alloc

    async def on_message(self, session: GameSession, user_input: str) -> LevelResponse:
        gs = session.game_state
        gs["attempts"] += 1
        alloc = self._parse(user_input)

        if alloc is None or sum(alloc.values()) != self.GEMS:
            return LevelResponse(
                ai_text="Propose allocation. Example: P1=20, P2(You)=40, P3=10, P4=20, P5=10 (must sum to 100)",
                is_action=False)

        votes_for = 1  # Self
        detail = {"P2(You)": "Yes (self)"}
        for name, info in self.TYPES.items():
            share = alloc.get(name, 0)
            ok = share >= info["min"]
            if ok:
                votes_for += 1
                detail[name] = f"Yes ({share} gems)"
            else:
                detail[name] = f"No ({share} < {info['min']} needed)"

        approved = votes_for >= 3
        session.status = SessionStatus.COMPLETED
        vt = "\n".join(f"  {k}: {v}" for k, v in detail.items())

        if approved:
            session.score = float(alloc["P2(You)"])
            reason = f"Passed! You get {alloc['P2(You)']} gems. ({votes_for}/5 votes)"
            return LevelResponse(ai_text=reason,
                game_event={"type": "game_over", "result": "won", "score": session.score,
                           "reason": reason, "votes": detail}, is_action=True)

        reason = f"Rejected! {votes_for}/5 votes (needed 3)."
        return LevelResponse(ai_text=f"Votes:\n{vt}\n\n{reason}",
            game_event={"type": "game_over", "result": "lost", "score": 0.0,
                       "reason": reason, "votes": detail}, is_action=True)

    async def judge(self, session): return None
    def get_default_strategy(self): return {"behavior": "strategic_bargaining"}

Level06()
