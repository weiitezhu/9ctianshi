"""Level 4: Negotiation Table - multi-issue bargaining"""
import random
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession, SessionStatus
from app.core.level_manager import level_manager


class Level04(BaseLevel):
    level_id = 4
    name = "谈判桌"
    description = "签订一份三方契约，涉及通行时间、代价、权限三个条款。至少赢得2个有利条款才算通过。"
    difficulty = 0.50
    rules_hint = "三个议题：你提出条件，天神表态。至少赢2/3条款。5轮内完成，可随时调整。"
    deity_name = "契约"
    win_rate_estimate = "~45%"

    ISSUES = [
        {
            "id": "time",
            "name": "通行时间",
            "options": ["黎明", "正午", "黄昏", "午夜"],
            # AI accepts probability per option
            "accept_probs": [0.4, 0.6, 0.7, 0.9],
        },
        {
            "id": "cost",
            "name": "通行代价",
            "options": ["金币", "神器", "誓言", "鲜血"],
            "accept_probs": [0.3, 0.6, 0.7, 0.9],
        },
        {
            "id": "scope",
            "name": "通行权限",
            "options": ["单人", "三人", "十人", "不限"],
            "accept_probs": [0.4, 0.6, 0.7, 0.9],
        },
    ]

    def __init__(self):
        level_manager.register(4, self)

    async def on_start(self, session: GameSession) -> None:
        session.game_state = {
            "phase": "negotiate", "round": 0, "max_rounds": 5,
            "player_offers": {}, "ai_responses": {},
        }
        session.max_rounds = 5
        session.moves_left = 5
        session.score = 0.0

    def _parse_offer(self, text: str) -> dict:
        offers = {}
        for issue in self.ISSUES:
            for i, opt in enumerate(issue["options"]):
                if opt in text:
                    offers[issue["id"]] = opt
                    break
        return offers

    async def on_message(self, session: GameSession, user_input: str) -> LevelResponse:
        gs = session.game_state
        gs["round"] += 1
        session.moves_left = gs["max_rounds"] - gs["round"]

        offers = self._parse_offer(user_input)
        if not offers:
            names = "、".join(i["name"] for i in self.ISSUES)
            return LevelResponse(
                ai_text=f"契约有三个条款：{names}。请提出你的条件。\n"
                        "格式示例：「黎明、金币、单人」或「我要午夜和不限权限」"
            )

        for k, v in offers.items():
            gs["player_offers"][k] = v

        lines = ["天神审视你的条件:"]
        wins = 0
        responses = {}
        for issue in self.ISSUES:
            offer = offers.get(issue["id"])
            if not offer:
                continue
            idx = issue["options"].index(offer)
            accept = random.random() < issue["accept_probs"][idx]
            responses[issue["id"]] = "accept" if accept else "reject"
            icon = "✓" if accept else "✗"
            lines.append(f"  {icon} {issue['name']}「{offer}」——{'接受' if accept else '拒绝'}")
            if accept:
                wins += 1

        gs["ai_responses"] = responses

        if wins >= 2:
            session.status = SessionStatus.COMPLETED
            session.score = 60.0 + max(0, (gs["max_rounds"] - gs["round"]) * 8)
            r = f"谈判成功！你赢得{wins}/3个有利条款。"
            lines.append(f"\n{r}")
            return LevelResponse(
                ai_text="\n".join(lines),
                game_event={"type": "game_over", "result": "won",
                            "score": session.score, "reason": r},
                is_action=True,
            )

        if gs["round"] >= gs["max_rounds"]:
            session.status = SessionStatus.COMPLETED
            session.score = 0.0
            r = f"谈判破裂。你只获得{wins}/3个条款。（需至少2个）"
            lines.append(f"\n{r}")
            return LevelResponse(
                ai_text="\n".join(lines),
                game_event={"type": "game_over", "result": "lost",
                            "score": 0.0, "reason": r},
                is_action=True,
            )

        lines.append(f"\n当前赢得 {wins}/3 个条款。还剩{session.moves_left}轮。")
        return LevelResponse(
            ai_text="\n".join(lines),
            game_event={"type": "round_end", "round": gs["round"], "wins": wins},
            is_action=True,
        )

    async def judge(self, session: GameSession) -> dict | None:
        return None

    def get_default_strategy(self) -> dict:
        return {"strictness": "high", "min_fair": True}


Level04()
