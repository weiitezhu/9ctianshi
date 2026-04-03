"""
九重天试 - 交互式 CLI 客户端
直接调用后端 REST API，无需额外依赖
"""
import sys
import urllib.request
import urllib.error
import json
import os
import time
import getpass

# ── 配置 ──────────────────────────────────────────
BASE_URL = "http://127.0.0.1:8000"
CLEAR = "cls" if os.name == "nt" else "clear"
# ──────────────────────────────────────────────────


def clear_screen():
    os.system(CLEAR)


def api_get(path: str) -> dict | None:
    try:
        req = urllib.request.Request(BASE_URL + path)
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except urllib.error.URLError:
        return None


def api_post(path: str, data: dict) -> dict | None:
    try:
        body = json.dumps(data).encode()
        req = urllib.request.Request(
            BASE_URL + path, data=body,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.URLError:
        return None


# ── 装饰：打印标题 ────────────────────────────────
def heading(text: str, sub: str = ""):
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + text.center(58) + "║")
    if sub:
        print("║" + sub.center(58) + "║")
    print("╚" + "═" * 58 + "╝")


def rule(text: str):
    print("  " + "─" * 56)
    print("  " + text)


def ok(text: str):
    print("  ✅ " + text)


def info(text: str):
    print("  ℹ  " + text)


def warn(text: str):
    print("  ⚠  " + text)


def bold(text: str):
    print("  " + "\033[1m" + text + "\033[0m")


def ai_says(text: str):
    """打印天神的回应，带引号装饰"""
    print()
    print("  ┌" + "─" * 56 + "┐")
    for line in _wrap(text, 54):
        print("  │ " + line.ljust(54) + " │")
    print("  └" + "─" * 56 + "┘")


def _wrap(text: str, width: int) -> list:
    """简单自动换行"""
    lines = []
    for para in text.split("\n"):
        while len(para) > width:
            lines.append(para[:width])
            para = para[width:]
        if para:
            lines.append(para)
    return lines or [""]


# ── 关卡列表 ──────────────────────────────────────
LEVELS = [
    (1, "谎言之门", "⭐⭐", "谛听", "~70%",
     "两扇门，一真一假。天神给提示，但提示未必为真。"),
    (2, "囚徒之局", "⭐⭐", "裁决", "~55%",
     "5轮合作/背叛，天神以眼还眼。"),
    (3, "分金博弈", "⭐⭐⭐", "分配", "~50%",
     "100枚金币，你分配，天神决定是否接受。"),
    (4, "谈判桌", "⭐⭐⭐", "契约", "~45%",
     "3条款5轮谈判，至少赢2个。"),
    (5, "信任之桥", "⭐⭐⭐", "信守", "~40%",
     "双方同时选择建桥，5轮通过3次。"),
    (6, "海盗分金", "⭐⭐⭐⭐", "分配", "~35%",
     "你是第2号海盗，分配100颗宝石，过半同意才通过。"),
    (7, "谎言猎手", "⭐⭐⭐⭐", "真言", "~30%",
     "8条信息，3条是假的，用你的智慧找出来。"),
    (8, "镜中对决", "⭐⭐⭐⭐⭐", "镜像", "~25%",
     "剑·盾·镜7轮对决，天神会学习你的模式。"),
    (9, "天神之局", "⭐⭐⭐⭐⭐", "本尊", "~15%",
     "终极三关：真相之门→献祭抉择→最终审判。"),
]


# ── 主流程 ────────────────────────────────────────
def main():
    clear_screen()
    heading("九 重 天 试", "AI 天神 vs 人类 博弈游戏")
    print()
    print("  欢迎，凡人。你将踏入九重天的试炼之地。")
    print("  每关一位天神，各自设局。")
    print("  用你的智慧、策略与洞察，征服九重天。")
    print()

    player_id = getpass.getpass("  请输入你的名字（或昵称）：").strip()
    if not player_id:
        player_id = "挑战者"

    player_id = f"cli_{player_id}_{int(time.time())}"

    while True:
        clear_screen()
        heading("九 重 天 试", f"当前挑战者：{player_id}")
        _show_levels()
        print()
        choice = input("  选择关卡（1-9），或输入 q 退出：").strip()

        if choice.lower() in ("q", "quit", "exit"):
            print("\n  后会有期，凡人。\n")
            break

        if not choice.isdigit() or not (1 <= int(choice) <= 9):
            warn("无效选择，请输入 1-9")
            time.sleep(1)
            continue

        level_id = int(choice)
        _play_level(player_id, level_id)


def _show_levels():
    print("  " + "┌──┬────────────┬──────┬────────┬──────────┬──────────────────────────────┐")
    print("  " + "│关│    名称    │难度  │  天神  │ 预估胜率 │  简介                       │")
    print("  " + "├──┼────────────┼──────┼────────┼──────────┼──────────────────────────────┤")
    for (lid, name, diff, deity, win, desc) in LEVELS:
        desc_short = desc[:20] + "…" if len(desc) > 20 else desc
        print(f"  │{lid:2}│{name:12s}│{diff:6s}│{deity:8s}│{win:10s}│{desc_short:28s}│")
    print("  " + "└──┴────────────┴──────┴────────┴──────────┴──────────────────────────────┘")


def _play_level(player_id: str, level_id: int):
    clear_screen()
    lid, name, diff, deity, win, desc = LEVELS[level_id - 1]

    heading(f"第 {lid} 关：{name}", f"天神：{deity}  |  {diff}  |  预估胜率：{win}")
    print()
    rule("【规则】")
    print("  " + desc)
    print()
    info("正在连接天神，请稍候...")
    print()

    # 开始游戏
    result = api_post("/api/game/start", {"player_id": player_id, "level_id": level_id})
    if not result:
        warn("⚠  后端服务未启动。请先运行：")
        warn("   cd backend && .venv\\Scripts\\python -m uvicorn app.main:app --port 8000")
        input("\n  按回车返回...")
        return

    session_id = result.get("session_id", "?")
    opening = result.get("opening_message", "...")
    rules_hint = result.get("rules_hint", "")

    ok(f"游戏开始！Session: {session_id[:20]}...")
    print()
    if opening:
        ai_says(opening)
    if rules_hint:
        print("  💡 提示：" + rules_hint)

    # 游戏循环
    round_num = 1
    while True:
        print()
        print("  ── " + f"第 {round_num} 轮" + " " + "─" * 44)
        user_input = input("\n  你：").strip()

        if not user_input:
            continue

        if user_input in ("退出", "quit", "exit", "q"):
            print("\n  你选择了退出本关。")
            break

        if user_input in ("重开", "restart", "r"):
            _play_level(player_id, level_id)
            return

        if user_input in ("状态", "status", "s"):
            status = api_get(f"/api/game/status/{player_id}")
            if status:
                print(f"  状态：{status.get('status')}  |  分数：{status.get('score',0)}")
                print(f"  回合：{status.get('current_round',0)}/{status.get('max_rounds',0)}")
                print(f"  剩余：{status.get('moves_left',0)}")
            continue

        # 发消息
        resp = api_post("/api/game/message", {"player_id": player_id, "content": user_input})
        if not resp:
            warn("网络错误，请检查后端是否运行中。")
            continue

        # 处理响应
        game_event = resp.get("game_event") or resp.get("events", [{}])[0] if resp.get("events") else None
        ai_text = resp.get("ai_text") or resp.get("content") or ""

        if ai_text:
            ai_says(ai_text)

        if game_event:
            etype = game_event.get("type", "")
            if etype == "game_over":
                result = game_event.get("result", "?")
                score = game_event.get("score", 0)
                reason = game_event.get("reason", "")

                print()
                if result == "won":
                    print("  ╔══════════════════════════════════════════════════════════╗")
                    print("  ║               🎉  恭喜！你通过了本关！                    ║")
                    print(f"  ║                    得分：{score:.0f}                              ║")
                    print("  ╚══════════════════════════════════════════════════════════╝")
                elif result == "tie":
                    print("  ╔══════════════════════════════════════════════════════════╗")
                    print("  ║               ⚖️   平局！再接再厉。                      ║")
                    print(f"  ║                    得分：{score:.0f}                              ║")
                    print("  ╚══════════════════════════════════════════════════════════╝")
                else:
                    print("  ╔══════════════════════════════════════════════════════════╗")
                    print("  ║               ❌  挑战失败。                              ║")
                    print(f"  ║                    得分：{score:.0f}                              ║")
                    if reason:
                        print(f"  ║               原因：{reason[:40]}  ║")
                    print("  ╚══════════════════════════════════════════════════════════╝")

                print()
                again = input("  输入任意内容返回选关，r 键重玩本关：").strip()
                if again.lower() == "r":
                    _play_level(player_id, level_id)
                return

            elif etype == "round_end":
                info(f"回合结束。剩余回合：{game_event.get('moves_left', '?')}")
            elif etype == "question_asked":
                info(f"天神收到你的问题。剩余提问：{game_event.get('remaining', '?')}")
            elif etype == "facts_shown":
                info("天神展示了全部信息。")
            elif etype == "phase_complete":
                info(f"阶段完成！结果：{game_event.get('result')}，进入：{game_event.get('next_phase', '')}")

        round_num += 1
        if round_num > 30:
            warn("游戏超过30轮，强制结束。")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\n  下次见，凡人。")
