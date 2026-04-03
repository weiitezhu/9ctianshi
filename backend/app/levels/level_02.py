"""Level 2: Prisoner's Dilemma - Repeated game"""
import random
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession, SessionStatus
from app.core.level_manager import level_manager


class Level02(BaseLevel):
    """5 rounds of simultaneous Cooperate/Betray. Tit-for-tat AI with noise."""

    level_id = 2
    name = "Prisoner's Dilemma"
    description = "You and the deity simultaneously choose: Cooperate or Betray. 5 rounds, highest total score wins."
    difficulty = 0.30
    rules_hint = "Each round: both choose simultaneously. Cooperate=3/3, Mutual Betray=1/1, One Betrays=5/0."
    deity_name = "The Arbiter"
    win_rate_estimate = "~55%"

    PAYOFFS = {
        ("Cooperate", "Cooperate"): (3, 3),
        ("Cooperate", "Betray"): (0, 5),
        ("Betray", "Cooperate"): (5, 0),
        ("Betray", "Betray"): (1, 1),
    }

    def __init__(self):
        level_manager.register(2, self)

    async def on_start(self, session: GameSession) -> None:
        session.game_state = {
            "round": 0, "max_rounds": 5,
            "player_total": 0, "ai_total": 0, "history": [],
        }
        session.max_rounds = 5
        session.moves_left = 5
        session.score = 0.0

    def _extract_choice(self, text: str) -> str | None:
        t = text.strip().lower()
        if "betray" in t: return "Betray"
        if "cooperate" in t or "coop" in t: return "Cooperate"
        return None

    async def on_message(self, session: GameSession, user_input: str) -> LevelResponse:
        gs = session.game_state
        gs["round"] += 1
        session.moves_left = gs["max_rounds"] - gs["round"]

        choice = self._extract_choice(user_input)
        if not choice:
            return LevelResponse(ai_text="Choose: Cooperate or Betray?", is_action=False)

        ai_choice = self._ai_decide(gs)
        p_pay, a_pay = self.PAYOFFS[(choice, ai_choice)]
        gs["player_total"] += p_pay
        gs["ai_total"] += a_pay
        gs["history"].append({"r": gs["round"], "p": choice, "a": ai_choice, "pp": p_pay, "ap": a_pay})
        session.score = gs["player_total"]

        txt = f"Round {gs['round']}: You {choice}, Deity {ai_choice}. Scores: You +{p_pay}, Deity +{a_pay}"

        if gs["round"] >= gs["max_rounds"]:
            session.status = SessionStatus.COMPLETED
            pt, at = gs["player_total"], gs["ai_total"]
            if pt > at:
                session.score, rc, reason = 100.0, "won", f"You win {pt}:{at}!"
            elif pt == at:
                session.score, rc, reason = 50.0, "tie", f"Tied at {pt} each."
            else:
                session.score, rc, reason = 0.0, "lost", f"Deity wins {at}:{pt}."
            return LevelResponse(ai_text=txt + f"\n\n{reason}",
                game_event={"type": "game_over", "result": rc, "score": session.score,
                           "reason": reason, "final": f"{pt}:{at}"}, is_action=True)

        return LevelResponse(ai_text=txt + f"\n{session.moves_left} rounds left.",
            game_event={"type": "round_end", "round": gs["round"]}, is_action=True)

    def _ai_decide(self, gs):
        h = gs.get("history", [])
        if not h: return random.choices(["Cooperate", "Betray"], weights=[0.6, 0.4])[0]
        if random.random() < 0.8: return h[-1]["p"]  # Tit-for-tat
        return random.choice(["Cooperate", "Betray"])

    async def judge(self, session): return None

    def get_default_strategy(self):
        return {"behavior": "tit_for_tat_with_noise", "initial_coop": 0.6}

Level02()
