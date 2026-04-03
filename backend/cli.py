"""
九重天试 - 交互式 CLI
设计目标：
  - 直接从第一关开始，无需选关
  - AI 生成每关的独特场景和选项
  - 玩家自由输入，AI 判断结果
  - 失败自动重试本关，成功自动进入下一关
  - 简洁、有仪式感的 UI
"""
import sys
import os
import urllib.request
import urllib.error
import json
import time

BASE = "http://127.0.0.1:8000"
PLAYER_ID = f"player_{int(time.time())}"


# ── API helpers ─────────────────────────────────────
def api_get(path):
    try:
        req = urllib.request.Request(BASE + path)
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except urllib.error.URLError:
        return None


def api_post(path, data):
    try:
        body = json.dumps(data).encode()
        req = urllib.request.Request(
            BASE + path, data=body,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.URLError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


# ── UI helpers ──────────────────────────────────────
C = "\033[92m"    # green  - AI good
R = "\033[91m"    # red    - error / lose
Y = "\033[93m"   # yellow - hint
B = "\033[94m"   # blue   - scene
M = "\033[95m"   # magenta - level title
W = "\033[0m"    # reset
BOLD = "\033[1m"
CLEAR = "cls" if os.name == "nt" else "clear"


def clear():
    os.system(CLEAR)


def hr(width=70, char="─"):
    print(f"  {char * width}")


def title(text):
    print(f"\n  {M}{BOLD}{text}{W}")


def ai(text):
    """Print AI (deity) response"""
    if not text:
        return
    print(f"\n  {C}◆ 天神：{W}")
    for line in text.split("\n"):
        line = line.strip()
        if line:
            print(f"    {C}{line}{W}")


def scene(text):
    """Print scene description"""
    if not text:
        return
    print(f"\n  {B}▸ 场景：{W} {text}")


def options(opts):
    """Print options from AI"""
    if not opts:
        return
    print(f"\n  {Y}◆ 可选行动：{W}")
    for o in opts:
        key = o.get("key", "?")
        txt = o.get("text", "")
        print(f"    {Y}[{key}]{W} {txt}")


def hint(text):
    """Print hint"""
    if text:
        print(f"  {Y}💡 {text}{W}")


def status(rounds_left, score):
    print(f"  剩余回合：{rounds_left}  |  当前得分：{score:.0f}")


def banner(level_id, level_name):
    titles = {
        1: "谎言之门", 2: "囚徒之局", 3: "分金博弈",
        4: "谈判桌",   5: "信任之桥", 6: "海盗分金",
        7: "谎言猎手", 8: "镜中对决", 9: "天神之局",
    }
    names = {
        1: "谛听", 2: "裁决", 3: "分配",
        4: "契约", 5: "信守", 6: "分配",
        7: "真言", 8: "镜像", 9: "本尊",
    }
    difficulties = {
        1: "★☆☆☆☆", 2: "★★☆☆☆", 3: "★★★☆☆",
        4: "★★★☆☆", 5: "★★★★☆", 6: "★★★★☆",
        7: "★★★★★", 8: "★★★★★", 9: "★★★★★",
    }
    t = titles.get(level_id, f"第{level_id}关")
    n = names.get(level_id, "?")
    d = difficulties.get(level_id, "")
    print()
    print(f"  ╔{'═' * 62}╗")
    print(f"  ║  第 {level_id} 关  {t:<20}  天神：{n:<8} {d}  ║")
    print(f"  ╚{'═' * 62}╝")


def win_screen(level_id, score):
    print()
    print(f"  {C}{BOLD}✦ ✦ ✦  恭喜通关！✦ ✦ ✦{W}")
    print(f"  {C}你征服了第{level_id}关！得分：{score:.0f}{W}")
    if level_id < 9:
        next_titles = {
            1: "囚徒之局", 2: "分金博弈", 3: "谈判桌",
            4: "信任之桥", 5: "海盗分金", 6: "谎言猎手",
            7: "镜中对决", 8: "天神之局",
        }
        print(f"  即将进入：{M}{next_titles.get(level_id, '下一关')}{W}…")
        time.sleep(2)
    else:
        print()
        print(f"  {C}{BOLD}★★★ 九重天试，全部通关！★★★{W}")
        print(f"  {C}你是真正的胜者！{W}")
    print()


def lose_screen(level_id):
    print()
    print(f"  {R}{BOLD}✗ ✗ ✗  挑战失败 ✗ ✗ ✗{W}")
    print(f"  {R}第{level_id}关，你需要重新尝试。{W}")
    print()


def intro(text):
    """Print level intro"""
    if text:
        print(f"\n  {M}◇ {text}{W}")


# ── Main game loop ──────────────────────────────────
def main():
    clear()
    print()
    print(f"  {M}{BOLD}╔═══════════════════════════════════════════════════════════╗{W}")
    print(f"  {M}{BOLD}║                                                           ║{W}")
    print(f"  {M}{BOLD}║            九  重  天  试                                 ║{W}")
    print(f"  {M}{BOLD}║        AI 天神  vs  人类  博弈游戏                        ║{W}")
    print(f"  {M}{BOLD}║                                                           ║{W}")
    print(f"  {M}{BOLD}╚═══════════════════════════════════════════════════════════╝{W}")
    print()
    print(f"  欢迎，凡人。九重天的试炼，从第一关开始。")
    print(f"  天神会为你设置独特场景，你用自然语言自由选择。")
    print(f"  失败重来，成功进入下一关。九关皆过，你便是胜者。")
    print()
    input(f"  {Y}按回车开始…{W}")

    # ── Game loop: level by level ──
    current_level = 1
    consecutive_fails = 0

    while current_level <= 9:
        clear()
        banner(current_level, "")

        # Start this level
        r = api_post("/api/game/start",
                     {"player_id": PLAYER_ID, "level_id": current_level})
        if "error" in r:
            print(f"\n  {R}⚠ 无法连接后端。确保后端已启动（uvicorn app.main:app --port 8000）{W}")
            return

        intro(r.get("level_intro", ""))
        scene(r.get("scene_text", ""))
        options(r.get("options", []))
        hint(r.get("hint", ""))
        status(r.get("rounds_left", "?"), r.get("score", 0))

        # ── Play this level ──
        failed_this_level = False
        while True:
            print()
            try:
                raw = input(f"  {BOLD}你说：{W} ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n\n  后会有期。\n")
                return

            if not raw:
                continue

            resp = api_post("/api/game/act",
                           {"player_id": PLAYER_ID, "content": raw})

            if "error" in resp:
                print(f"  {R}错误: {resp['error']}{W}")
                continue

            t = resp.get("type", "continue")

            if t == "game_over":
                result = resp.get("result", "lost")
                score = resp.get("score", 0)

                # Show AI's final response
                ai_text = resp.get("ai_text", "")
                if ai_text:
                    ai(ai_text)

                if result == "won":
                    win_screen(current_level, score)
                    consecutive_fails = 0
                    current_level += 1
                    break   # → next level
                else:
                    lose_screen(current_level)
                    consecutive_fails += 1
                    if consecutive_fails >= 3:
                        print(f"  {Y}提示：你似乎遇到困难。试试更谨慎的选择，或者输入'hint'获取提示。{W}")
                    break   # → retry same level

            elif t == "continue":
                # Show scene update
                if resp.get("ai_text"):
                    ai(resp["ai_text"])
                if resp.get("scene_text"):
                    scene(resp["scene_text"])
                options(resp.get("options", []))
                hint(resp.get("hint", ""))
                status(resp.get("rounds_left", "?"), resp.get("score", 0))

        # Check if all levels done
        if current_level > 9:
            break

    # End screen
    clear()
    print()
    print(f"  {C}{BOLD}★★★ 九重天试，全部通关！★★★{W}")
    print(f"  {C}你用智慧与勇气征服了九位天神。{W}")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  下次见，凡人。\n")
