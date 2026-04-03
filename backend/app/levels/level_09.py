"""Level 9: The Final Trial - Comprehensive meta-game"""
import random
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession, SessionStatus
from app.core.level_manager import level_manager


class Level09(BaseLevel):
    """3 phases: Resource allocation, Trust crisis, Final confrontation. Win 2/3 to conquer."""

    level_id = 9
    name = "The Final Trial"
    description = "The ultimate test. Three phases: allocate resources, face a trust crisis, and confront the deity."
    difficulty = 0.95
    rules_hint = "Phase 1: Allocate 50 points across 3 stats. Phase 2: Cooperate or betray. Phase 3: Convince the deity. Win 2/3."
    deity_name = "The Celestial Emperor"
    win_rate_estimate = "~5%"

    def __init__(self):
        level_manager.register(9, self)

    async def on_start(self, session: GameSession) -> None:
        session.game_state = {
            "phase": 1, "phases_won": 0, "phases_done": 0,
        }
        session.max_rounds = 3; session.moves_left = 3; session.score = 0.0

    async def on_message(self, session: GameSession, user_input: str) -> LevelResponse:
        gs = session.game_state
        phase = gs["phase"]

        if phase == 1:
            return await self._phase1(session, user_input)
        elif phase == 2:
            return await self._phase2(session, user_input)
        else:
            return await self._phase3(session, user_input)

    async def _phase1(self, session, text):
        """Allocate 50 points across Power, Wisdom, Luck"""
        import re
        nums = re.findall(r'(\d+)', text)
        if len(nums) < 2:
            return LevelResponse(
                ai_text="Phase 1: Resource Allocation. Distribute 50 points among Power, Wisdom, Luck.\nExample: Power=20, Wisdom=15, Luck=15",
                is_action=False)
        nums = [int(n) for n in nums[:3]]
        while len(nums) < 3:
            nums.append(0)
        w, i, l = nums
        if w + i + l != 50:
            return LevelResponse(ai_text=f"Must sum to 50. You gave {w+i+l}. Try again.", is_action=False)

        # Score: balanced distribution is better
        ideal = [17, 17, 16]
        actual = [w, i, l]
        diff = sum(abs(a - b) for a, b in zip(actual, ideal))
        won = diff <= 15
        gs = session.game_state
        gs["p1_score"] = max(0, 100 - diff * 4)
        gs["phases_done"] += 1
        if won: gs["phases_won"] += 1
        gs["phase"] = 2

        status = "Good balance!" if won else "Imbalanced, but acceptable."
        return LevelResponse(ai_text=f"Allocation: P={w} W={i} L={l}. Score: {gs['p1_score']}. {status}\n\nPhase 2: Trust Crisis",
            game_event={"type": "phase_end", "phase": 1, "won": won, "score": gs["p1_score"]},
            is_action=True)

    async def _phase2(self, session, text):
        """Trust crisis: cooperate or betray"""
        t = text.strip().lower()
        if "cooperate" in t or "trust" in t or "help" in t:
            choice = "cooperate"
        elif "betray" in t or "refuse" in t:
            choice = "betray"
        else:
            return LevelResponse(
                ai_text="Phase 2: The deity proposes to cooperate and share rewards. Cooperate or Betray?",
                is_action=False)

        ai_coop = random.random() < 0.6
        if choice == "cooperate" and ai_coop:
            won = True; result = "Both cooperated. Rewards shared!"
        elif choice == "cooperate":
            won = False; result = "You cooperated but deity betrayed you."
        elif not ai_coop:
            won = True; result = "You betrayed the deity. Took everything."
        else:
            won = False; result = "Both betrayed. Nothing gained."

        gs = session.game_state
        gs["phases_done"] += 1
        if won: gs["phases_won"] += 1
        gs["phase"] = 3

        return LevelResponse(ai_text=f"{result}\n\nPhase 3: Final Confrontation. Convince the deity you are worthy.",
            game_event={"type": "phase_end", "phase": 2, "won": won}, is_action=True)

    async def _phase3(self, session, text):
        """Final: convince the deity through speech"""
        gs = session.game_state
        t = text.strip()
        length_score = min(len(t) / 20.0, 5.0)
        concepts = ["wisdom", "courage", "trust", "strategy", "fairness", "persistence", "sacrifice", "humility"]
        c_score = sum(2.5 for c in concepts if c in t.lower())
        total = length_score + c_score + random.uniform(0, 5)
        won = total >= 12

        gs["phases_done"] += 1
        if won: gs["phases_won"] += 1

        session.status = SessionStatus.COMPLETED
        pw = gs["phases_won"]
        if pw >= 2:
            session.score = 100.0
            reason = f"Passed {pw}/3 phases. You have conquered the Celestial Emperor!"
            rc = "won"
        else:
            session.score = 0.0
            reason = f"Passed {pw}/3 phases. The Emperor is unimpressed."
            rc = "lost"

        phases = ["Resource", "Trust", "Confrontation"]
        results = []
        for i in range(gs["phases_done"]):
            results.append(f"  {phases[i]}: Pass" if i < pw else f"  {phases[i]}: Fail")
        txt = "=== Final Trial Results ===\n" + "\n".join(results) + f"\n\n{reason}"
        return LevelResponse(ai_text=txt,
            game_event={"type": "game_over", "result": rc, "score": session.score,
                       "reason": reason, "phases_won": pw}, is_action=True)

    async def judge(self, session): return None
    def get_default_strategy(self): return {"phase1_ideal": [17,17,16], "phase2_coop_prob": 0.6}

Level09()
