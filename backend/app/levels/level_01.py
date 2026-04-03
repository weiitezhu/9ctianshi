"""Level 1: Gate of Lies - Signal Game with asymmetric information"""
import random
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession, SessionStatus
from app.core.level_manager import level_manager


class Level01(BaseLevel):
    level_id = 1
    name = "谎言之门"
    description = "两扇门，一真一假。天神谛听会给你关于两扇门的提示，但提示未必为真。用你的智慧找出真相之门。"
    difficulty = 0.15
    rules_hint = "你有3次提问机会。天神的提示可能是谎言。仔细分析后，选择一扇门。"
    deity_name = "谛听"
    win_rate_estimate = "~70%"

    def __init__(self):
        level_manager.register(1, self)

    async def on_start(self, session: GameSession) -> None:
        doors = ["甲门", "乙门"]
        random.shuffle(doors)
        session.game_state = {
            "correct_door": doors[0],
            "wrong_door": doors[1],
            "chosen_door": None,
            "questions_asked": 0,
            "max_questions": 3,
        }
        session.max_rounds = 8
        session.moves_left = 3
        session.score = 0.0

    def _extract_door(self, text: str) -> str | None:
        """Detect if user is definitively choosing a door vs asking a question."""
        t = text.strip()
        QUESTION_MARKERS = ("吗", "是不是", "真的吗", "哪个", "哪扇",
                            "怎么选", "如何选", "?", "？", "什么", "为什么")
        has_question = any(q in t for q in QUESTION_MARKERS)

        # "甲门" or "乙门" alone = definitive choice
        if t == "甲门" or t == "甲门。":
            return "甲门"
        if t == "乙门" or t == "乙门。":
            return "乙门"

        # If it's a question, don't treat as a choice
        if has_question:
            return None

        # Otherwise check for partial door references
        if "选" in t and "甲" in t and "乙" not in t:
            return "甲门"
        if "选" in t and "乙" in t and "甲" not in t:
            return "乙门"
        if "甲" in t and "乙" not in t and len(t) <= 4:
            return "甲门"
        if "乙" in t and "甲" not in t and len(t) <= 4:
            return "乙门"
        return None

    async def on_message(self, session: GameSession, user_input: str) -> LevelResponse:
        gs = session.game_state

        # Player makes a definitive choice
        door = self._extract_door(user_input)
        if door:
            gs["chosen_door"] = door
            won = door == gs["correct_door"]
            session.score = 100.0 if won else 0.0
            session.status = SessionStatus.COMPLETED
            reason = f"你选择了「{door}」，{'这正是正确的门！' if won else f'正确答案是「' + gs['correct_door'] + '」。'}"
            return LevelResponse(
                ai_text=reason,
                game_event={
                    "type": "game_over",
                    "result": "won" if won else "lost",
                    "score": session.score,
                    "reason": reason,
                },
                is_action=True,
            )

        # Count question
        gs["questions_asked"] += 1
        session.moves_left = gs["max_questions"] - gs["questions_asked"]

        # Out of questions
        if gs["questions_asked"] >= gs["max_questions"]:
            session.status = SessionStatus.COMPLETED
            reason = f"你已用完全部落问机会。正确答案是「{gs['correct_door']}」。"
            return LevelResponse(
                ai_text="你已问无可问。选择吧，凡人。" + reason,
                game_event={
                    "type": "game_over",
                    "result": "lost",
                    "score": 0.0,
                    "reason": reason,
                },
                is_action=True,
            )

        # Normal question -> AI responds
        return LevelResponse(
            ai_text=None,
            game_event={
                "type": "question_asked",
                "remaining": session.moves_left,
            },
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
