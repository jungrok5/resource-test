"""End-to-end tests that require a real Aseprite binary.

Skipped automatically when Aseprite is not installed. Run scripts/setup-aseprite.sh
first (or set ASEPRITE_PATH) to enable them.
"""

import shutil

import pytest

from aseprite_mcp.core.commands import AsepriteError, aseprite_binary
from aseprite_mcp.tools import canvas, drawing, export

try:
    from aseprite_mcp.core.commands import ensure_aseprite_available

    ensure_aseprite_available()
    HAS_ASEPRITE = True
except AsepriteError:
    HAS_ASEPRITE = False

pytestmark = pytest.mark.skipif(
    not HAS_ASEPRITE, reason=f"Aseprite binary not found ({aseprite_binary()})"
)


async def test_full_sprite_workflow(tmp_path):
    sprite = str(tmp_path / "hero.aseprite")
    png = str(tmp_path / "hero.png")

    result = await canvas.create_canvas(8, 8, sprite)
    assert "8x8" in result

    await drawing.draw_rectangle(sprite, 0, 0, 8, 8, "#3366ff", fill=True)
    await drawing.draw_pixels(sprite, [{"x": 3, "y": 3, "color": "#ff0000"}])
    await drawing.draw_line(sprite, 0, 7, 7, 0, "#00ff00")

    info = await canvas.get_sprite_info(sprite)
    assert "size: 8x8" in info
    assert "frames: 1" in info

    await export.export_sprite(sprite, png, scale=2)

    with open(png, "rb") as handle:
        header = handle.read(24)
    assert header[:8] == b"\x89PNG\r\n\x1a\n"
    width = int.from_bytes(header[16:20], "big")
    height = int.from_bytes(header[20:24], "big")
    assert (width, height) == (16, 16)


async def test_animation_workflow(tmp_path):
    sprite = str(tmp_path / "anim.aseprite")
    gif = str(tmp_path / "anim.gif")
    sheet = str(tmp_path / "anim-sheet.png")

    await canvas.create_canvas(4, 4, sprite)
    await drawing.fill_area(sprite, 0, 0, "#000000", frame=1)
    await canvas.add_frame(sprite, duration_ms=120)
    await drawing.fill_area(sprite, 0, 0, "#ffffff", frame=2)

    info = await canvas.get_sprite_info(sprite)
    assert "frames: 2" in info

    await export.export_sprite(sprite, gif)
    with open(gif, "rb") as handle:
        assert handle.read(6) in (b"GIF87a", b"GIF89a")

    await export.export_spritesheet(sprite, sheet, columns=2)
    with open(sheet, "rb") as handle:
        header = handle.read(24)
    assert header[:8] == b"\x89PNG\r\n\x1a\n"
    assert int.from_bytes(header[16:20], "big") == 8  # 2 frames of 4px side by side


async def test_run_lua_script(tmp_path):
    sprite = str(tmp_path / "lua.aseprite")
    await canvas.create_canvas(5, 5, sprite)
    output = await export.run_lua_script(
        "print(app.sprite.width * app.sprite.height)", sprite
    )
    assert output.strip() == "25"
