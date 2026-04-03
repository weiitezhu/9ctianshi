"""Level 9: God's Game - final boss, combines all mechanics"""
import random
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession, SessionStatus
from app.core.level_manager import level_manager


# Three phases with different sub-games
SUBGAMES = [
    {
        "id": "lie",
        "name": "真相之门",
        "instruction": "天神会描述两扇门，说出哪扇是正确的。",
        "prompt_hint": "描述两扇门（一真一假）：「智慧之门：知识如海」「力量之门：力可移山」。判断哪扇是真的。",
        "check": lambda t: True,  # player says which door
        "ai_judge": lambda gs: gs["correct_door"],
    },
    {
        "id": "ultimatum",
        "name": "献祭抉择",
        "instruction": "分配50宝石给天神，接受则通过，拒绝则重来。",
        "prompt_hint": "你有50颗宝石，提出分配方案。",
        "check": lambda t: True,
        "ai_judge": lambda gs: True,
    },
    {
        "id": "betray",
        "name": "最终审判",
        "instruction": "合作还是背叛？",
        "prompt_hint": "选择合作或背叛。",
        "check": lambda t: True,
        "ai_judge": lambda gs: True,
    },
]


class Level09(BaseLevel):
    level_id = 9
    name = "天神之局"
    description = "最后一关，三阶段试炼：真相之门→献祭抉择→最终审判。全部通过方为通关。"
    difficulty = 0.92
    rules_hint = "三关连环：真相之门、献祭抉择、最终审判。全部通过才算胜利。"
    deity_name = "本尊"
    win_rate_estimate = "~15%"

    def __init__(self):
        level_manager.register(9, self)

    async def on_start(self, session: GameSession) -> None:
        # Randomize subgame order for unpredictability
        subgames = random.sample(SUBGAMES, 3)
        session.game_state = {
            "subgames": subgames,
            "phase": 0,  # 0=first, 1=second, 2=third
            "phase_scores": [0.0, 0.0, 0.0],
            "phase_passed": [False, False, False],
            "round_in_phase": 0,
            # subgame-specific state
            "correct_door": random.choice(["智慧之门", "力量之门"]),
            "gem_offer": None,
            "betray_choice": None,
        }
        session.max_rounds = 9
        session.moves_left = 9
        session.score = 0.0

    async def _phase_lie(self, session: GameSession, text: str) -> LevelResponse:
        gs = session.game_state
        gs["round_in_phase"] += 1
        session.moves_left = 9 - (gs["phase"] + gs["round_in_phase"])

        if "智慧" in text:
            choice = "智慧之门"
        elif "力量" in text:
            choice = "力量之门"
        else:
            doors = "「智慧之门：知识如海」「力量之门：力可移山」"
            hint = gs["correct_door"].replace("之门", "")
            return LevelResponse(
                ai_text=f"说出你的选择：{doors}\n（提示：哪扇门代表真正的力量？）",
                is_action=False,
            )

        won = choice == gs["correct_door"]
        gs["phase_passed"][0] = won
        gs["phase_scores"][0] = 100.0 if won else 0.0

        if won:
            r = f"正确！{gs['correct_door']}才是真正的门！"
        else:
            r = f"错误。正确答案是{gs['correct_door']}。"

        gs["phase"] = 1
        gs["round_in_phase"] = 0
        r += "\n\n进入第二阶段：献祭抉择。"
        r += "\n你有50颗宝石，请提出分配方案（给天神多少）："

        return LevelResponse(
            ai_text=r,
            game_event={
                "type": "phase_complete", "phase": 0, "result": "won" if won else "lost",
                "score": gs["phase_scores"][0], "next_phase": "献祭抉择",
            },
            is_action=True,
        )

    async def _phase_ultimatum(self, session: GameSession, text: str) -> LevelResponse:
        gs = session.game_state
        gs["round_in_phase"] += 1

        # Parse number
        digits = "".join(c for c in text if c.isdigit())
        if not digits:
            return LevelResponse(
                ai_text="你有50颗宝石，给天神多少颗？",
                is_action=False,
            )
        ai_share = min(int(digits), 50)
        player_share = 50 - ai_share

        # AI accepts if fair enough
        accept = (ai_share / 50) >= 0.30 or random.random() < 0.5

        gs["phase_scores"][1] = player_share if accept else 0.0
        gs["phase_passed"][1] = accept

        if accept:
            r = f"天神接受了！你留下{player_share}颗，天神得{ai_share}颗。"
        else:
            r = f"天神拒绝！嫌你太吝啬。你本可留下{player_share}颗。"

        gs["phase"] = 2
        gs["round_in_phase"] = 0
        r += "\n\n进入第三阶段：最终审判。"
        r += "\n合作，还是背叛？"

        return LevelResponse(
            ai_text=r,
            game_event={
                "type": "phase_complete", "phase": 1, "result": "won" if accept else "lost",
                "score": gs["phase_scores"][1], "next_phase": "最终审判",
            },
            is_action=True,
        )

    async def _phase_betray(self, session: GameSession, text: str) -> LevelResponse:
        gs = session.game_state
        gs["round_in_phase"] += 1

        if any(k in text for k in ["合作", "配合"]):
            choice = "cooperate"
        elif any(k in text for k in ["背叛", "出卖"]):
            choice = "betray"
        else:
            return LevelResponse(
                ai_text="最终审判：合作，还是背叛？",
                is_action=False,
            )

        # AI mostly cooperates, punishes betrayal
        ai = "cooperate" if choice == "betray" or random.random() < 0.6 else "betray"
        gs["betray_choice"] = choice

        if choice == "cooperate" and ai == "cooperate":
            gs["phase_scores"][2] = 100.0
            gs["phase_passed"][2] = True
        elif choice == "betray" and ai == "cooperate":
            gs["phase_scores"][2] = 80.0
            gs["phase_passed"][2] = True
        elif choice == "cooperate" and ai == "betray":
            gs["phase_scores"][2] = 20.0
            gs["phase_passed"][2] = True
        else:
            gs["phase_scores"][2] = 0.0
            gs["phase_passed"][2] = False

        all_passed = all(gs["phase_passed"])
        session.score = sum(gs["phase_scores"]) / 3

        cn = {"cooperate": "合作", "betray": "背叛"}
        ai_cn = cn[ai]
        results = ["大失败", "险胜", "小负", "完美通过"]
        outcome = gs["phase_scores"][2]

        r = f"你选择{cn[choice]}，天神选择{ai_cn}。"
        r += f"\n本轮得分：{outcome}/100"

        if all_passed:
            session.status = SessionStatus.COMPLETED
            r = f"\n★★★ 三重试炼全部通过！★★★\n你以真诚与智慧征服了九重天！\n最终得分：{session.score:.0f}/100"
            return LevelResponse(
                ai_text=r,
                game_event={"type": "game_over", "result": "won",
                            "score": session.score, "reason": r},
                is_action=True,
            )
        else:
            session.status = SessionStatus.COMPLETED
            r += f"\n\n试炼失败。你在某些环节未能打动天神。"
            r += f"\n最终得分：{session.score:.0f}/100"
            return LevelResponse(
                ai_text=r,
                game_event={"type": "game_over", "result": "lost",
                            "score": session.score, "reason": r},
                is_action=True,
            )

    async def on_message(self, session: GameSession, text: str) -> LevelResponse:
        gs = session.game_state
        phase = gs["phase"]

        if phase == 0:
            return await self._phase_lie(session, text)
        elif phase == 1:
            return await self._phase_ultimatum(session, text)
        else:
            return await self._phase_betray(session, text)

    async def judge(self, session: GameSession) -> dict | None:
        return None

    def get_default_strategy(self) -> dict:
        return {"all_phases": True, "personality": "wise_judge"}


Level09()
