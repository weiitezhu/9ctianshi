"""Level 7: Lie Hunter - find 3 fake statements among 8"""
import random
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession, SessionStatus
from app.core.level_manager import level_manager


class Level07(BaseLevel):
    level_id = 7
    name = "谎言猎手"
    description = "天神给出8条信息，其中3条是假的。你通过提问和推理找出所有假信息。AI会根据你的追问动态调整谎言。"
    difficulty = 0.72
    rules_hint = "8条信息，3条是假的。说出编号指出假信息。AI会监控你的推理过程并调整策略。"
    deity_name = "真言"
    win_rate_estimate = "~30%"

    FACTS = [
        "天神的坐骑是一匹白鹿。",
        "试炼之地的入口在东方。",
        "通关钥匙藏在第三个房间。",
        "天神的弱点是音乐。",
        "试炼的时间限制是两个时辰。",
        "天神每天午时会休息一刻钟。",
        "通过试炼的人都会忘记这段经历。",
        "天神其实同情所有挑战者。",
    ]
    # Ground truth: 2=cannot find key in third room (key location unknown),
    # 4=music is NOT weakness (random), 6=not all forget (some remember)
    FAKE_GROUND = {2, 4, 6}

    def __init__(self):
        level_manager.register(7, self)

    async def on_start(self, session: GameSession) -> None:
        idxs = list(range(len(self.FACTS)))
        random.shuffle(idxs)
        fake_set = set(random.sample(idxs, 3))
        ordered = [self.FACTS[i] for i in idxs]
        # Map position -> ground truth index
        pos_to_ground = {pos: idxs[pos] for pos in range(len(idxs))}

        session.game_state = {
            "facts": ordered,
            "fake_grounds": {pos_to_ground[p] for p in range(len(ordered)) if pos_to_ground[p] in fake_set},
            "discovered": set(),  # positions discovered as fake
            "questioned": 0,
            "max_questions": 10,
        }
        session.max_rounds = 10
        session.moves_left = 10
        session.score = 0.0

    async def on_message(self, session: GameSession, user_input: str) -> LevelResponse:
        gs = session.game_state
        gs["questioned"] += 1
        session.moves_left = gs["max_questions"] - gs["questioned"]

        t = user_input.strip()

        # Check for "第N条是假的/错的"
        found = None
        for i in range(len(gs["facts"])):
            mark = f"第{i+1}条" in t or f"{i+1}条" in t
            if mark and any(k in t for k in ["假", "错", "伪", "不真"]):
                found = i
                break

        if found is not None:
            if found in gs["discovered"]:
                return LevelResponse(
                    ai_text=f"第{found+1}条已经识破了。",
                    game_event={"remaining": session.moves_left},
                    is_action=True,
                )
            gs["discovered"].add(found)
            total_fakes = len(gs["fake_grounds"])
            if len(gs["discovered"]) >= total_fakes:
                session.status = SessionStatus.COMPLETED
                session.score = max(100.0 - gs["questioned"] * 5, 20.0)
                r = f"全部{total_fakes}条假信息已识破！"
                return LevelResponse(
                    ai_text=r,
                    game_event={"type": "game_over", "result": "won",
                                "score": session.score, "reason": r},
                    is_action=True,
                )
            left = total_fakes - len(gs["discovered"])
            return LevelResponse(
                ai_text=f"正确！还剩{left}条。",
                game_event={"found": len(gs["discovered"]), "total": total_fakes},
                is_action=True,
            )

        # First two rounds: show all facts
        if gs["questioned"] <= 2:
            lines = ["天神列出以下信息："]
            for i, f in enumerate(gs["facts"]):
                lines.append(f"  {i+1}. {f}")
            lines.append("\n请指出你认为假的信息，格式：「第3条是假的」")
            return LevelResponse(
                ai_text="\n".join(lines),
                game_event={"type": "facts_shown"},
                is_action=True,
            )

        # Ran out
        if session.moves_left <= 0:
            session.status = SessionStatus.COMPLETED
            session.score = 0.0
            r = f"时间耗尽。你只找出了{len(gs['discovered'])}/{len(gs['fake_grounds'])}条。"
            return LevelResponse(
                ai_text=r,
                game_event={"type": "game_over", "result": "lost",
                            "score": 0.0, "reason": r},
                is_action=True,
            )

        return LevelResponse(
            ai_text=None,
            game_event={"type": "question_asked", "remaining": session.moves_left},
            is_action=False,
        )

    async def judge(self, session: GameSession) -> dict | None:
        return None

    def get_default_strategy(self) -> dict:
        return {"defensive": True, "adapt": True, "lie_smart": True}


Level07()
