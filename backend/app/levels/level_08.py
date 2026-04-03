"""Level 8: Mirror Duel - meta-game where AI mirrors and counter-strategies"""
import random
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession, SessionStatus
from app.core.level_manager import level_manager


class Level08(BaseLevel):
    level_id = 8
    name = "镜中对决"
    description = "你在镜中面对一个模仿你的对手。每轮双方同时出：剑、盾、镜。克制关系：剑克盾、盾克镜、镜克剑（反弹）。\n但AI会分析你的出招模式并预判。"
    difficulty = 0.80
    rules_hint = "出剑/盾/镜。7轮中赢4轮。AI会学习你的模式——保持不可预测。"
    deity_name = "镜像"
    win_rate_estimate = "~25%"

    MOVES = ["剑", "盾", "镜"]
    # move A beats move at index BEATS[A]
    BEATS = {"剑": "盾", "盾": "镜", "镜": "剑"}  # key beats value

    def __init__(self):
        level_manager.register(8, self)

    async def on_start(self, session: GameSession) -> None:
        session.game_state = {
            "round": 0, "max_rounds": 7, "need_wins": 4,
            "player_wins": 0, "ai_wins": 0, "draws": 0,
            "history": [],  # list of (player_move, ai_move)
        }
        session.max_rounds = 7
        session.moves_left = 7
        session.score = 0.0

    def _parse(self, text: str) -> str | None:
        t = text.strip()
        for m in self.MOVES:
            if m in t:
                return m
        if "出" in t:
            for m in self.MOVES:
                if m in t:
                    return m
        return None

    def _ai_choose(self, gs: dict) -> str:
        """AI with pattern recognition + counter-strategy"""
        history = gs.get("history", [])
        if len(history) < 2:
            return random.choice(self.MOVES)

        # Analyze player patterns
        last3 = [h[0] for h in history[-3:]]
        # Predict next move (most frequent in last 3)
        from collections import Counter
        freq = Counter(last3)
        predicted = freq.most_common(1)[0][0]

        # Counter the predicted move
        predicted_beats = self.BEATS[predicted]
        # We need to beat what they'll play
        for m, beats in self.BEATS.items():
            if beats == predicted:
                counter = m
                break
        else:
            counter = predicted_beats

        # 60% use counter, 30% random, 10% mirror
        r = random.random()
        if r < 0.60:
            return counter
        elif r < 0.90:
            return random.choice(self.MOVES)
        else:
            return history[-1][0]  # mirror

    def _resolve(self, p: str, a: str) -> str:
        """Returns 'player', 'ai', or 'draw'"""
        if p == a:
            return "draw"
        if self.BEATS[p] == a:
            return "player"
        return "ai"

    async def on_message(self, session: GameSession, user_input: str) -> LevelResponse:
        gs = session.game_state
        move = self._parse(user_input)
        if not move:
            return LevelResponse(
                ai_text="请选择你的招式：剑、盾、镜。\n"
                        "克制关系：剑克盾、盾克镜、镜克剑。"
            )

        gs["round"] += 1
        session.moves_left = gs["max_rounds"] - gs["round"]

        ai = self._ai_choose(gs)
        result = self._resolve(move, ai)
        gs["history"].append((move, ai))

        if result == "player":
            gs["player_wins"] += 1
        elif result == "ai":
            gs["ai_wins"] += 1
        else:
            gs["draws"] += 1

        cn = {"player": "你赢了", "ai": "天神赢了", "draw": "平局"}
        text = f"第{gs['round']}轮：你出「{move}」，天神出「{ai}」→ {cn[result]}"
        text += f"\n比分：你 {gs['player_wins']} - {gs['ai_wins']} 天神（平{gs['draws']}）"

        # Check early win
        rounds_left = gs["max_rounds"] - gs["round"]
        if gs["player_wins"] >= gs["need_wins"]:
            session.status = SessionStatus.COMPLETED
            session.score = 100.0
            r = f"你以{gs['player_wins']}:{gs['ai_wins']}获胜！"
            return LevelResponse(
                ai_text=text + f"\n{r}",
                game_event={"type": "game_over", "result": "won",
                            "score": 100.0, "reason": r},
                is_action=True,
            )

        if gs["ai_wins"] > rounds_left or (gs["max_rounds"] - gs["round"] + gs["player_wins"] < gs["need_wins"]):
            # Can't catch up
            pass

        if gs["round"] >= gs["max_rounds"]:
            session.status = SessionStatus.COMPLETED
            won = gs["player_wins"] >= gs["need_wins"]
            session.score = 100.0 if won else 0.0
            r = "你赢了！" if won else f"天神以{gs['ai_wins']}:{gs['player_wins']}获胜。"
            return LevelResponse(
                ai_text=text + f"\n{r}",
                game_event={"type": "game_over", "result": "won" if won else "lost",
                            "score": session.score, "reason": r},
                is_action=True,
            )

        return LevelResponse(
            ai_text=text + f"\n还需赢{gs['need_wins'] - gs['player_wins']}轮。",
            game_event={"type": "round_end", "round": gs["round"]},
            is_action=True,
        )

    async def judge(self, session: GameSession) -> dict | None:
        return None

    def get_default_strategy(self) -> dict:
        return {"pattern_recognition": True, "counter_rate": 0.6}


Level08()
