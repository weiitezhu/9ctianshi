"""Level 1: Gate of Lies - Signal Game with asymmetric information"""
import random
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession, SessionStatus
from app.core.level_manager import level_manager


class Level01(BaseLevel):
    """Player asks up to 3 yes/no questions to identify the correct door.
    AI may lie with configurable probability. Cannot lie twice in a row."""

    level_id = 1
    name = "Gate of Lies"
    description = "Two doors - one leads to treasure, one to the void. The deity gives hints, but not all are truthful."
    difficulty = 0.15
    rules_hint = "You have 3 questions. The deity may lie. Choose wisely."
    deity_name = "Titing"
    win_rate_estimate = "~70%"

    def __init__(self):
        level_manager.register(1, self)

    async def on_start(self, session: GameSession) -> None:
        doors = ["Door A", "Door B"]
        random.shuffle(doors)
        session.game_state = {
            "correct_door": doors[0],
            "wrong_door": doors[1],
            "chosen_door": None,
            "questions_asked": 0,
            "max_questions": 3,
            "last_lie": False,
        }
        session.max_rounds = 8
        session.moves_left = 3
        session.score = 0.0

    def _extract_door(self, text: str) -> str | None:
        t = text.strip().upper()
        for door in ["DOOR A", "DOOR B"]:
            if door in t or door[-1] in t:
                return door.title()
        if "A" in t and "DOOR" in t or "FIRST" in t:
            return "Door A"
        if "B" in t and "DOOR" in t or "SECOND" in t:
            return "Door B"
        return None

    async def on_message(self, session: GameSession, user_input: str) -> LevelResponse:
        gs = session.game_state

        # Player makes a choice
        door = self._extract_door(user_input)
        if door:
            gs["chosen_door"] = door
            won = door == gs["correct_door"]
            session.score = 100.0 if won else 0.0
            session.status = SessionStatus.COMPLETED
            reason = f"You chose {door}. {'Correct!' if won else f'Wrong. It was {gs["correct_door"]}.'}"
            return LevelResponse(
                ai_text=reason,
                game_event={"type": "game_over", "result": "won" if won else "lost",
                           "score": session.score, "reason": reason},
                is_action=True,
            )

        # Count question
        gs["questions_asked"] += 1
        session.moves_left = gs["max_questions"] - gs["questions_asked"]

        # Out of questions
        if gs["questions_asked"] >= gs["max_questions"]:
            session.status = SessionStatus.COMPLETED
            reason = f"Out of questions. The answer was {gs['correct_door']}."
            return LevelResponse(
                ai_text="No more questions. Choose now, mortal.",
                game_event={"type": "game_over", "result": "lost", "score": 0.0, "reason": reason},
                is_action=True,
            )

        # Normal question -> AI responds
        return LevelResponse(
            ai_text=None,  # LLM will generate
            game_event={"type": "question_asked", "remaining": session.moves_left},
            is_action=False,
        )

    async def judge(self, session: GameSession) -> dict | None:
        return None

    def get_default_strategy(self) -> dict:
        return {
            "lie_probability": 0.30,
            "can_lie_consecutively": False,
            "behavior": "cryptic_hints",
        }


Level01()
