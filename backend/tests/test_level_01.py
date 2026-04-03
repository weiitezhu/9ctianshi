"""Test Level 1 logic"""
import asyncio
from app.levels.level_01 import Level01
from app.core.session_manager import GameSession, SessionStatus


def test_level01_start():
    level = Level01()
    session = GameSession(level_id=1)
    strategy = level.get_default_strategy()

    assert strategy["lie_probability"] == 0.30
    assert strategy["can_lie_consecutively"] is False


def test_level01_choose_correct():
    level = Level01()
    session = GameSession(level_id=1)

    # Manually set correct door for testing
    session.game_state["correct_door"] = "甲门"
    session.game_state["wrong_door"] = "乙门"

    result = asyncio.get_event_loop().run_until_complete(
        level.handle_action(session, "choose_door", "我选甲门")
    )

    assert result["type"] == "game_over"
    assert result["result"] == "won"
    assert result["score"] == 100


def test_level01_choose_wrong():
    level = Level01()
    session = GameSession(level_id=1)

    session.game_state["correct_door"] = "甲门"
    session.game_state["wrong_door"] = "乙门"

    result = asyncio.get_event_loop().run_until_complete(
        level.handle_action(session, "choose_door", "我选乙门")
    )

    assert result["type"] == "game_over"
    assert result["result"] == "lost"


if __name__ == "__main__":
    test_level01_start()
    test_level01_choose_correct()
    test_level01_choose_wrong()
    print("All tests passed!")
