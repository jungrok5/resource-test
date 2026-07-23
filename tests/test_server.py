"""Smoke tests that don't require Aseprite to be installed."""

import pytest

from aseprite_mcp import mcp
from aseprite_mcp.core.commands import (
    AsepriteError,
    lua_color,
    lua_quote,
    parse_color,
    run_script,
)

EXPECTED_TOOLS = {
    "create_canvas",
    "add_frame",
    "add_layer",
    "get_sprite_info",
    "draw_pixels",
    "draw_line",
    "draw_rectangle",
    "draw_ellipse",
    "fill_area",
    "export_sprite",
    "export_spritesheet",
    "run_lua_script",
}


async def test_all_tools_registered():
    tools = await mcp.list_tools()
    assert {tool.name for tool in tools} == EXPECTED_TOOLS


def test_parse_color_variants():
    assert parse_color("#ff0000") == (255, 0, 0, 255)
    assert parse_color("00ff00") == (0, 255, 0, 255)
    assert parse_color("#0000ff80") == (0, 0, 255, 128)
    assert parse_color("#fff") == (255, 255, 255, 255)


def test_parse_color_invalid():
    with pytest.raises(ValueError):
        parse_color("#12345")
    with pytest.raises(ValueError):
        parse_color("#zzzzzz")


def test_lua_helpers():
    assert lua_color("#102030") == "Color{r=16, g=32, b=48, a=255}"
    assert lua_quote('a"b\\c') == '"a\\"b\\\\c"'


def test_missing_binary_raises(monkeypatch, tmp_path):
    monkeypatch.setenv("ASEPRITE_PATH", str(tmp_path / "definitely-not-aseprite"))
    with pytest.raises(AsepriteError, match="not found"):
        run_script("print('hi')")
