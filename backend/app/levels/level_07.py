"""Level 7: Lie Hunter - Information warfare / Deduction"""
import random
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession, SessionStatus
from app.core.level_manager import level_manager


class Level07(BaseLevel):
    """8 facts, 3 are fake. Player asks questions and identifies fakes. 12 question limit."""

    level_id = 7
    name = "Lie Hunter"
    description = "8 facts from the deity, 3 are lies. Deduce which ones through questioning."
    difficulty = 0.72
    rules_hint = "8 facts, 3 are fake. Ask questions or identify fakes by number. 12 questions max."
    deity_name = "The Oracle"
    win_rate_estimate = "~30%"

    FACTS = [
        "The deity rides a white deer.",
        "The trial entrance faces east.",
        "The key is in the third room.",
        "The deity's weakness is music.",
        "The trial has a 2-hour time limit.",
        "The deity rests at noon for 15 minutes.",
        "Those who pass forget the experience.",
        "The deity pities all challengers.",
        "The northern lake has healing water.",
        "The deity's palace has 999 lamps.",
        "Failed challengers turn to stone.",
        "The deity favors autumn above all.",
    ]

    def __init__(self):
        level_manager.register(7, self)

    async def on_start(self, session: GameSession) -> None:
        selected = random.sample(self.FACTS, 8)
        fakes = set(random.sample(range(8), 3))
        session.game_state = {
            "facts": selected, "fakes": fakes, "found": set(),
            "questions": 0, "max_q": 12, "shown": False,
        }
        session.max_rounds = 12; session.moves_left = 12; session.score = 0.0

    async def on_message(self, session: GameSession, user_input: str) -> LevelResponse:
        gs = session.game_state
        t = user_input.strip()
        gs["questions"] += 1
        session.moves_left = gs["max_q"] - gs["questions"]

        # First: show facts
        if not gs["shown"]:
            gs["shown"] = True
            txt = "8 facts (3 are fake):\n\n"
            for i, f in enumerate(gs["facts"]):
                txt += f"{i+1}. {f}\n"
            txt += "\nIdentify fakes by number: "#3 is fake""
            return LevelResponse(ai_text=txt, is_action=True, game_event={"type": "facts_shown"})

        # Try to identify a fake
        import re
        nums = re.findall(r'#?(\d+)', t)
        is_claim = any(w in t for w in ["fake", "lie", "false", "wrong"])
        if nums and is_claim:
            idx = int(nums[0]) - 1
            if 0 <= idx < 8:
                if idx in gs["fakes"]:
                    gs["found"].add(idx)
                    found = len(gs["found"])
                    needed = len(gs["fakes"])
                    if found >= needed:
                        session.status = SessionStatus.COMPLETED
                        session.score = max(100.0 - gs["questions"] * 5, 20.0)
                        return LevelResponse(
                            ai_text=f"All {needed} fakes found in {gs['questions']} questions!",
                            game_event={"type": "game_over", "result": "won",
                                       "score": session.score,
                                       "reason": f"Found all fakes"}, is_action=True)
                    return LevelResponse(
                        ai_text=f"Correct! {needed - found} fakes remaining.",
                        game_event={"type": "fake_found", "found": found, "total": needed},
                        is_action=True)
                else:
                    return LevelResponse(
                        ai_text=f"#{idx+1} is TRUE: {gs['facts'][idx]}",
                        is_action=True)

        # Out of questions
        if gs["questions"] >= gs["max_q"]:
            session.status = SessionStatus.COMPLETED; session.score = 0.0
            return LevelResponse(
                ai_text=f"Time up. Found {len(gs['found'])}/{len(gs['fakes'])} fakes.",
                game_event={"type": "game_over", "result": "lost", "score": 0.0,
                           "reason": "Out of questions"}, is_action=True)

        # Normal question -> AI responds
        return LevelResponse(ai_text=None,
            game_event={"type": "question_asked", "remaining": session.moves_left},
            is_action=False)

    async def judge(self, session): return None
    def get_default_strategy(self):
        return {"defensive": True, "redirect": True, "adapt": True}

Level07()
