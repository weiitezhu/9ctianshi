"""Level 4: The Negotiation Table - Multi-issue bargaining"""
import random
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession, SessionStatus
from app.core.level_manager import level_manager


class Level04(BaseLevel):
    """3 issues to negotiate. Need 2/3 accepted within 5 rounds."""

    level_id = 4
    name = "Negotiation Table"
    description = "Negotiate a contract with 3 clauses: Time, Price, Access. Win 2/3 to pass."
    difficulty = 0.50
    rules_hint = "Each round, propose all 3 clauses. The deity accepts or rejects each. 5 rounds to win 2/3."
    deity_name = "The Contract"
    win_rate_estimate = "~45%"

    ISSUES = [
        {"id": "time", "name": "Passage Time", "opts": ["Dawn", "Noon", "Dusk", "Midnight"]},
        {"id": "price", "name": "Price", "opts": ["Gold", "Artifact", "Oath", "Blood"]},
        {"id": "access", "name": "Access Level", "opts": ["Solo", "Three", "Ten", "Unlimited"]},
    ]

    def __init__(self):
        level_manager.register(4, self)

    async def on_start(self, session: GameSession) -> None:
        session.game_state = {"round": 0, "max_rounds": 5, "offers": {}, "results": []}
        session.max_rounds = 5; session.moves_left = 5; session.score = 0.0

    def _parse(self, text: str) -> dict:
        offers = {}
        for issue in self.ISSUES:
            for opt in issue["opts"]:
                if opt.lower() in text.lower():
                    offers[issue["id"]] = opt; break
        return offers

    async def on_message(self, session: GameSession, user_input: str) -> LevelResponse:
        gs = session.game_state
        gs["round"] += 1
        session.moves_left = gs["max_rounds"] - gs["round"]
        offers = self._parse(user_input)

        if not offers:
            names = ", ".join(i["name"] for i in self.ISSUES)
            return LevelResponse(
                ai_text=f"Three clauses: {names}.\nExample: I want Dawn, Gold, Solo",
                is_action=False)

        wins = 0; results = []
        for issue in self.ISSUES:
            if issue["id"] not in offers: continue
            opt = offers[issue["id"]]
            if opt not in issue["opts"]: continue
            # AI prefers later options (harder for player to get accepted)
            idx = issue["opts"].index(opt)
            prob = 0.30 + idx * 0.15
            accepted = random.random() < prob
            if accepted: wins += 1
            results.append({"issue": issue["name"], "opt": opt, "ok": accepted})

        gs["results"].append(results)
        resp = "The deity reviews...\n"
        for r in results:
            resp += f"  [{'ACCEPT' if r['ok'] else 'REJECT'}] {r['issue']}: {r['opt']}\n"
        resp += f"\nThis round: {wins}/3 accepted."

        if wins >= 2:
            session.status = SessionStatus.COMPLETED
            bonus = (gs["max_rounds"] - gs["round"]) * 8
            session.score = 60.0 + bonus
            return LevelResponse(ai_text=f"Contract signed! {wins}/3 clauses won.",
                game_event={"type": "game_over", "result": "won", "score": session.score,
                           "reason": f"Won {wins}/3 clauses"}, is_action=True)

        if gs["round"] >= gs["max_rounds"]:
            session.status = SessionStatus.COMPLETED; session.score = 0.0
            return LevelResponse(ai_text="Negotiation failed.",
                game_event={"type": "game_over", "result": "lost", "score": 0.0,
                           "reason": "Failed to win 2/3 clauses"}, is_action=True)

        return LevelResponse(ai_text=resp + f"\n{session.moves_left} rounds left.",
            game_event={"type": "round_end", "round": gs["round"], "wins": wins}, is_action=True)

    async def judge(self, session): return None
    def get_default_strategy(self): return {"initial_strict": True, "concession_prob": 0.4}

Level04()
