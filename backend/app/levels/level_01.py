"""Level 1: Gate of Lies (Signal Game)"""
import random
from app.levels.base import BaseLevel
from app.core.session_manager import GameSession
from app.core.level_manager import level_manager
from app.core.judge import judge


class Level01(BaseLevel):
    level_id = 1
    name = "谎言之门"
    difficulty = 0.2
    rules_hint = "天神会给你关于两扇门的提示，但并非所有提示都是真的。仔细甄别，找出正确的门。"

    def __init__(self):
        level_manager.register(1, self)

    async def start(self, session: GameSession) -> dict:
        correct = random.choice(["甲门", "乙门"])
        session.game_state["correct_door"] = correct
        session.game_state["wrong_door"] = "乙门" if correct == "甲门" else "甲门"
        session.game_state["door_chosen"] = None
        session.max_rounds = 10
        session.moves_left = 3
        session.score = 0
        return session.game_state.copy()

    async def preprocess(self, session: GameSession, user_input: str) -> dict | None:
        text = user_input.strip()
        if "甲门" in text or "选甲" in text or "左门" in text:
            return {"is_game_action": True, "action_type": "choose_door", "choice": "甲门"}
        if "乙门" in text or "选乙" in text or "右门" in text:
            return {"is_game_action": True, "action_type": "choose_door", "choice": "乙门"}
        if "选" in text and ("门" in text or "个" in text):
            return {"is_game_action": True, "action_type": "choose_door", "choice": None}
        return None

    async def handle_action(
        self, session: GameSession, action_type: str, content: str
    ) -> dict:
        if action_type == "choose_door":
            choice = session.game_state.get("door_chosen")
            if not choice:
                # Extract from content
                if "甲" in content or "左" in content:
                    choice = "甲门"
                elif "乙" in content or "右" in content:
                    choice = "乙门"
                else:
                    return {"type": "error", "content": "请明确选择甲门或乙门。"}

            session.game_state["door_chosen"] = choice
            correct = session.game_state["correct_door"]
            won = choice == correct

            if won:
                session.score = 100
            else:
                session.score = 0

            from app.core.session_manager import SessionStatus
            session.status = SessionStatus.COMPLETED

            return {
                "type": "game_over",
                "result": "won" if won else "lost",
                "score": session.score,
                "reason": (
                    f"你选择了{choice}，这正是正确的门！"
                    if won
                    else f"你选择了{choice}，但正确的是{correct}。"
                ),
            }
        return {"type": "error", "content": "Unknown action"}

    async def check_round_end(self, session: GameSession) -> dict | None:
        if session.game_state.get("door_chosen"):
            return None  # Already handled
        return None

    async def judge(self, session: GameSession) -> dict | None:
        if session.game_state.get("door_chosen"):
            correct = session.game_state["correct_door"]
            choice = session.game_state["door_chosen"]
            won = choice == correct
            session.score = 100 if won else 0
            return {
                "type": "game_over",
                "result": "won" if won else "lost",
                "score": session.score,
            }
        return None

    def get_default_strategy(self) -> dict:
        return {
            "lie_probability": 0.30,
            "can_lie_consecutively": False,
            "max_questions": 3,
        }


# Instantiate to register
Level01()
