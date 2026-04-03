"""Judge system - win/lose determination"""
from app.core.session_manager import GameSession


class Judge:
    def rule_based_judge(self, session: GameSession, condition: dict) -> dict:
        score = session.score
        threshold = condition.get("threshold", 50)
        passed = score >= threshold
        return {
            "type": "game_over",
            "result": "won" if passed else "lost",
            "score": score,
            "reason": (
                f"Score {score} >= {threshold}"
                if passed
                else f"Score {score} < {threshold}"
            ),
        }


judge = Judge()
