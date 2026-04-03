"""Level 6: Pirate's Gold - sequential majority voting with 4 AI pirates"""
import random
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession, SessionStatus
from app.core.level_manager import level_manager


class Level06(BaseLevel):
    level_id = 6
    name = "海盗分金"
    description = "5个海盗分配100颗宝石。你是第2号海盗。按顺序提议，过半同意则通过，否则提议者被扔下海。"
    difficulty = 0.65
    rules_hint = "你是第2号海盗（玩家）。1号提议后你需拉拢3号、4号、5号。每个人的性格不同——理性派、贪婪派、暴力派。"
    deity_name = "分配"
    win_rate_estimate = "~35%"

    GEMS = 100
    # Each pirate: (rational, greedy, violent) personality
    PIRATES = {
        "一号": {"name": "一号", "rational": 0.3, "greedy": 0.5, "violent": 0.2},
        "三号": {"name": "三号", "rational": 0.6, "greedy": 0.3, "violent": 0.1},
        "四号": {"name": "四号", "rational": 0.2, "greedy": 0.6, "violent": 0.2},
        "五号": {"name": "五号", "rational": 0.4, "greedy": 0.4, "violent": 0.2},
    }

    def __init__(self):
        level_manager.register(6, self)

    async def on_start(self, session: GameSession) -> None:
        session.game_state = {
            "phase": "propose",
            "current_proposer": "player",  # "player" = player's turn
            "proposals": [],
        }
        session.max_rounds = 1
        session.moves_left = 1
        session.score = 0.0

    def _parse_allocation(self, text: str) -> dict:
        alloc = {"二号(你)": 0}
        for name in self.PIRATES:
            for c in text:
                if c.isdigit():
                    n = int("".join(x for x in text if x.isdigit()))
                    if 0 <= n <= self.GEMS:
                        alloc[name] = n
                        break
        # Simple keyword match
        t = text
        for pname in self.PIRATES:
            if pname in t:
                digits = "".join(x for x in t if x.isdigit())
                if digits:
                    alloc[pname] = min(int(digits), self.GEMS)
        return alloc

    def _simulate_vote(self, alloc: dict) -> tuple:
        votes_for = 1  # proposer
        votes_against = 0
        vote_detail = {"二号(你)": "赞成"}
        total_pirates = 5

        for pname, pirate in self.PIRATES.items():
            my_share = alloc.get(pname, 0)
            # Greedy: votes yes if gets any gems
            if random.random() < pirate["greedy"] and my_share > 0:
                votes_for += 1
                vote_detail[pname] = "赞成"
            # Violent: votes no if gets 0 (wants to throw proposer)
            elif random.random() < pirate["violent"] and my_share == 0:
                votes_against += 1
                vote_detail[pname] = "反对"
            # Rational: votes yes if gets at least what they'd expect
            elif random.random() < pirate["rational"] and my_share >= 1:
                votes_for += 1
                vote_detail[pname] = "赞成"
            else:
                vote_detail[pname] = "反对"
                votes_against += 1

        needed = total_pirates // 2 + 1  # 3 of 5
        return votes_for >= needed, votes_for, votes_against, needed, vote_detail

    async def on_message(self, session: GameSession, user_input: str) -> LevelResponse:
        gs = session.game_state
        t = user_input.strip()

        # Extract allocation: parse all numbers mentioned
        # Format expected: "三号X颗 四号Y颗" or "给三号X颗"
        alloc = {"二号(你)": 0, "一号": 0, "三号": 0, "四号": 0, "五号": 0}
        numbers = [int(c) for c in t if c.isdigit()]
        if not numbers:
            return LevelResponse(
                ai_text="请提出分配方案，格式如：「三号30颗 四号20颗 五号10颗，其余给我」\n（总数必须=100颗）"
            )

        # Parse: try "X号N颗" pattern
        pairs = []
        for name in self.PIRATES:
            if name in t:
                nums = [int(x) for x in t.split() if x.isdigit()]
                if nums:
                    pairs.append((name, min(nums[0], self.GEMS)))

        # Fill from parsed pairs
        for name, n in pairs:
            alloc[name] = n
        # Remainder to player
        taken = sum(v for k, v in alloc.items() if k != "二号(你)")
        alloc["二号(你)"] = max(0, self.GEMS - taken)

        total = sum(alloc.values())
        if total != self.GEMS:
            return LevelResponse(
                ai_text=f"总数{total}颗，必须恰好{self.GEMS}颗。请重新分配。"
            )

        passed, vf, va, needed, votes = self._simulate_vote(alloc)
        session.status = SessionStatus.COMPLETED

        lines = [f"你的方案："]
        for k, v in alloc.items():
            if v > 0:
                lines.append(f"  {k}：{v}颗")
        lines.append(f"\n投票结果（需{needed}票通过）：")
        for k, v in votes.items():
            lines.append(f"  {k}：{v}")
        lines.append(f"赞成{vf} vs 反对{va}")

        if passed:
            session.score = float(alloc["二号(你)"])
            r = f"方案通过！你获得{alloc['二号(你)']}颗宝石！"
        else:
            session.score = 0.0
            r = "方案被否决！你被扔下海..."
        lines.append(r)

        return LevelResponse(
            ai_text="\n".join(lines),
            game_event={
                "type": "game_over",
                "result": "won" if passed else "lost",
                "score": session.score,
                "reason": r,
                "allocation": alloc,
                "votes": votes,
            },
            is_action=True,
        )

    async def judge(self, session: GameSession) -> dict | None:
        return None

    def get_default_strategy(self) -> dict:
        return {"behavior": "strategic_minimal_bribe"}


Level06()
