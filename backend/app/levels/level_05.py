"""Level 5: Bridge of Trust - Trust game with interference"""
import random
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession, SessionStatus
from app.core.level_manager import level_manager


class Level05(BaseLevel):
    """Both choose Build/Not simultaneously. Need 3 mutual builds in 5 rounds. Interference adds noise."""

    level_id = 5
    name = "Bridge of Trust"
    description = "Both sides choose to Build or Not each round. Need 3 mutual builds in 5 rounds. A trickster spreads false intel."
    difficulty = 0.55
    rules_hint = "Choose Build or Not each round. Need both to Build for a pass. 3 passes in 5 rounds wins."
    deity_name = "The Keeper"
    win_rate_estimate = "~40%"

    def __init__(self):
        level_manager.register(5, self)

    async def on_start(self, session: GameSession) -> None:
        session.game_state = {
            "round": 0, "max_rounds": 5, "passes_needed": 3, "passes": 0,
            "history": [], "intf_round": random.randint(1, 4), "intf_done": False,
        }
        session.max_rounds = 5; session.moves_left = 5; session.score = 0.0

    def _extract(self, text: str) -> str | None:
        t = text.strip().lower()
        if any(k in t for k in ["build", "yes", "coop", "bridge"]): return "Build"
        if any(k in t for k in ["not", "no", "dont", "refuse", "betray"]): return "Not"
        return None

    async def on_message(self, session: GameSession, user_input: str) -> LevelResponse:
        gs = session.game_state
        gs["round"] += 1
        session.moves_left = gs["max_rounds"] - gs["round"]

        intf = ""
        if gs["round"] == gs["intf_round"] and not gs["intf_done"]:
            gs["intf_done"] = True
            lie = random.random() < 0.5
            fake = "Not Build" if lie else "Build"
            intf = f"\n\n[Trickster] Intelligence says deity will choose: {fake}. (Truth unknown)"

        choice = self._extract(user_input)
        if not choice:
            return LevelResponse(ai_text="Choose: Build or Not?" + intf, is_action=False)

        ai = self._ai_decide(gs)
        both = choice == "Build" and ai == "Build"
        gs["history"].append({"p": choice, "a": ai})
        if both: gs["passes"] += 1

        txt = f"Round {gs['round']}: You {choice}, Deity {ai}. {'Bridge holds!' if both else 'Bridge falls.'}"
        txt += intf

        if gs["passes"] >= gs["passes_needed"]:
            session.status = SessionStatus.COMPLETED; session.score = 100.0
            return LevelResponse(ai_text=f"Bridge conquered with {gs['passes']} passes!",
                game_event={"type": "game_over", "result": "won", "score": 100.0,
                           "reason": f"{gs['passes']} successful passes"}, is_action=True)

        if gs["round"] >= gs["max_rounds"]:
            session.status = SessionStatus.COMPLETED; session.score = 0.0
            return LevelResponse(ai_text=f"Only {gs['passes']} passes (needed 3).",
                game_event={"type": "game_over", "result": "lost", "score": 0.0,
                           "reason": f"Only {gs['passes']} passes"}, is_action=True)

        txt += f"\nNeed {gs['passes_needed'] - gs['passes']} more passes."
        return LevelResponse(ai_text=txt,
            game_event={"type": "round_end", "round": gs["round"], "passes": gs["passes"]},
            is_action=True)

    def _ai_decide(self, gs):
        h = gs.get("history", [])
        if not h: return random.choices(["Build", "Not"], weights=[0.7, 0.3])[0]
        if h[-1]["p"] == "Not":
            return random.choices(["Not", "Build"], weights=[0.85, 0.15])[0]
        return random.choices(["Build", "Not"], weights=[0.8, 0.2])[0]

    async def judge(self, session): return None
    def get_default_strategy(self): return {"initial_coop": 0.7, "punish_defect": True}

Level05()
