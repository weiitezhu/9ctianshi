"""Level 8: Mirror Duel - Meta game with pattern recognition"""
import random
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession, SessionStatus
from app.core.level_manager import level_manager


class Level08(BaseLevel):
    """RPS-style: Advance/Defend/Deceive. 5 rounds. Win 3+ to pass. AI uses pattern recognition."""

    level_id = 8
    name = "Mirror Duel"
    description = "Choose Advance, Defend, or Deceive each round. Rock-paper-scissors style. Win 3 of 5 rounds."
    difficulty = 0.82
    rules_hint = "Advance beats Deceive, Deceive beats Defend, Defend beats Advance. Win 3/5 rounds."
    deity_name = "The Mirror"
    win_rate_estimate = "~25%"
    MOVES = ["Advance", "Defend", "Deceive"]
    BEATS = {"Advance": "Deceive", "Deceive": "Defend", "Defend": "Advance"}
    MAX_R = 5
    WIN_NEED = 3

    def __init__(self):
        level_manager.register(8, self)

    async def on_start(self, session: GameSession) -> None:
        session.game_state = {
            "round": 0, "pw": 0, "aw": 0, "draws": 0, "history": [],
        }
        session.max_rounds = self.MAX_R; session.moves_left = self.MAX_R; session.score = 0.0

    def _extract(self, text: str) -> str | None:
        t = text.strip().lower()
        if "advance" in t or "attac" in t: return "Advance"
        if "defend" in t: return "Defend"
        if "deceive" in t or "bluf" in t: return "Deceive"
        return None

    def _resolve(self, p, a):
        if p == a: return "draw"
        return "player" if self.BEATS.get(p) == a else "ai"

    async def on_message(self, session: GameSession, user_input: str) -> LevelResponse:
        gs = session.game_state
        gs["round"] += 1
        session.moves_left = self.MAX_R - gs["round"]

        move = self._extract(user_input)
        if not move:
            return LevelResponse(ai_text="Choose: Advance, Defend, or Deceive?", is_action=False)

        ai = self._ai_decide(gs)
        result = self._resolve(move, ai)
        gs["history"].append({"r": gs["round"], "p": move, "a": ai, "res": result})

        if result == "player": gs["pw"] += 1; rtxt = f"You win!"
        elif result == "ai": gs["aw"] += 1; rtxt = "Deity wins."
        else: gs["draws"] += 1; rtxt = "Draw."

        txt = f"Round {gs['round']}: You {move} vs Deity {ai}. {rtxt}"

        # Early win
        if gs["pw"] >= self.WIN_NEED:
            session.status = SessionStatus.COMPLETED; session.score = 100.0
            return LevelResponse(ai_text=f"{txt}\n\nYou win the duel {gs['pw']}-{gs['aw']}!",
                game_event={"type": "game_over", "result": "won", "score": 100.0,
                           "reason": f"Won {gs['pw']}-{gs['aw']}"}, is_action=True)

        if gs["aw"] >= self.WIN_NEED:
            session.status = SessionStatus.COMPLETED; session.score = 0.0
            return LevelResponse(ai_text=f"{txt}\n\nDeity wins {gs['aw']}-{gs['pw']}.",
                game_event={"type": "game_over", "result": "lost", "score": 0.0,
                           "reason": f"Lost {gs['pw']}-{gs['aw']}"}, is_action=True)

        if gs["round"] >= self.MAX_R:
            session.status = SessionStatus.COMPLETED
            pw, aw = gs["pw"], gs["aw"]
            if pw > aw:
                session.score, rc, reason = 100.0, "won", f"You win {pw}-{aw}!"
            elif pw == aw:
                session.score, rc, reason = 50.0, "tie", f"Tied {pw}-{aw}."
            else:
                session.score, rc, reason = 0.0, "lost", f"Deity wins {aw}-{pw}."
            return LevelResponse(ai_text=f"{txt}\n\n{reason}",
                game_event={"type": "game_over", "result": rc, "score": session.score,
                           "reason": reason}, is_action=True)

        txt += f"\nScore: You {gs['pw']} - Deity {gs['aw']}"
        return LevelResponse(ai_text=txt,
            game_event={"type": "round_end", "round": gs["round"],
                       "score": f"{gs['pw']}-{gs['aw']}"}, is_action=True)

    def _ai_decide(self, gs):
        h = gs.get("history", [])
        if len(h) < 2: return random.choice(self.MOVES)
        # Detect repetition
        if h[-1]["p"] == h[-2]["p"]:
            target = h[-1]["p"]
            for m in self.MOVES:
                if self.BEATS.get(m) == target: return m
        # Counter last move
        last = h[-1]["p"]
        for m in self.MOVES:
            if self.BEATS.get(m) == last:
                return random.choices([m, random.choice(self.MOVES)], weights=[0.6, 0.4])[0]
        return random.choice(self.MOVES)

    async def judge(self, session): return None
    def get_default_strategy(self): return {"behavior": "pattern_recognition", "noise": 0.3}

Level08()
