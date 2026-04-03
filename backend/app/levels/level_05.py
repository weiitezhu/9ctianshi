"""Level 5: Bridge of Trust - simultaneous trust game with interference"""
import random
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession, SessionStatus
from app.core.level_manager import level_manager


class Level05(BaseLevel):
    level_id = 5
    name = "信任之桥"
    description = "每轮同时选择建桥或不建，双方都建才能通过。干扰者会散布真假情报。5轮内通过3次即可。"
    difficulty = 0.55
    rules_hint = "双方同时选建桥/不建。5轮需通3次。有干扰者会告诉你假消息。"
    deity_name = "信守"
    win_rate_estimate = "~40%"

    def __init__(self):
        level_manager.register(5, self)

    async def on_start(self, session: GameSession) -> None:
        session.game_state = {
            "round": 0, "max_rounds": 5, "need": 3, "passed": 0,
            "interference_round": random.randint(2, 4),
            "interference_shown": False, "history": [],
        }
        session.max_rounds = 5
        session.moves_left = 5
        session.score = 0.0

    def _parse(self, text: str) -> str | None:
        t = text.strip()
        if any(k in t for k in ["建桥", "建", "同意", "配合"]):
            return "build"
        if any(k in t for k in ["不建", "拒绝", "不配", "背叛"]):
            return "pass"
        return None

    def _ai_choose(self, gs: dict) -> str:
        h = gs.get("history", [])
        if not h:
            return random.choices(["build", "pass"], weights=[0.7, 0.3])[0]
        if h[-1]["player"] == "pass":
            return "pass"  # punish distrust
        return random.choices(["build", "pass"], weights=[0.8, 0.2])[0]

    async def on_message(self, session: GameSession, user_input: str) -> LevelResponse:
        gs = session.game_state
        gs["round"] += 1
        session.moves_left = gs["max_rounds"] - gs["round"]

        # Show interference
        extra = ""
        if gs["round"] == gs["interference_round"] and not gs["interference_shown"]:
            gs["interference_shown"] = True
            lie = random.random() < 0.5
            hint = "不建桥" if lie else "建桥"
            extra = f"\n【干扰者密报】据可靠消息，天神本轮打算「{hint}」。（真伪未知）"

        choice = self._parse(user_input)
        if not choice:
            return LevelResponse(ai_text="请选择：建桥，还是不建桥？" + extra)

        ai = self._ai_choose(gs)
        gs["history"].append({"round": gs["round"], "player": choice, "ai": ai})

        passed = (choice == "build" and ai == "build")
        if passed:
            gs["passed"] += 1

        cn = {"build": "建桥", "pass": "不建"}
        text = f"第{gs['round']}轮：你{cn[choice]}，天神{cn[ai]}。{'桥通了！' if passed else '桥未通。'}"
        text += extra

        if gs["passed"] >= gs["need"]:
            session.status = SessionStatus.COMPLETED
            session.score = 100.0
            r = f"信任之桥已通！成功通过{gs['passed']}次。"
            return LevelResponse(
                ai_text=text + f"\n{r}",
                game_event={"type": "game_over", "result": "won", "score": 100.0, "reason": r},
                is_action=True,
            )

        if gs["round"] >= gs["max_rounds"]:
            session.status = SessionStatus.COMPLETED
            session.score = 0.0
            r = f"5轮结束，你只通过了{gs['passed']}次。（需要{gs['need']}次）"
            return LevelResponse(
                ai_text=text + f"\n{r}",
                game_event={"type": "game_over", "result": "lost", "score": 0.0, "reason": r},
                is_action=True,
            )

        left = gs["need"] - gs["passed"]
        text += f"\n还需{left}次。"
        return LevelResponse(
            ai_text=text,
            game_event={"type": "round_end", "round": gs["round"], "passed": gs["passed"]},
            is_action=True,
        )

    async def judge(self, session: GameSession) -> dict | None:
        return None

    def get_default_strategy(self) -> dict:
        return {"initial_coop_prob": 0.70, "punish_defect": True}


Level05()
