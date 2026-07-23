"""Export and advanced scripting tools."""

from __future__ import annotations

import os

from ..core.commands import AsepriteError, run_command, run_script


async def export_sprite(
    filename: str, output_filename: str = "", scale: int = 1
) -> str:
    """Export a sprite to PNG/GIF/etc. GIF keeps animation frames.

    scale uses nearest-neighbor upscaling (pixel-art friendly).
    """
    path = os.path.abspath(filename)
    if not os.path.isfile(path):
        raise AsepriteError(f"Sprite file not found: {path}")
    if not output_filename:
        output_filename = os.path.splitext(path)[0] + ".png"
    out = os.path.abspath(output_filename)
    os.makedirs(os.path.dirname(out), exist_ok=True)

    args = [path]
    if scale != 1:
        if scale < 1:
            raise ValueError("scale must be >= 1")
        args += ["--scale", str(scale)]
    args += ["--save-as", out]
    run_command(args)
    return f"Exported {path} -> {out} (scale x{scale})"


async def export_spritesheet(
    filename: str, output_filename: str = "", columns: int = 0
) -> str:
    """Export all animation frames as a single sprite-sheet PNG."""
    path = os.path.abspath(filename)
    if not os.path.isfile(path):
        raise AsepriteError(f"Sprite file not found: {path}")
    if not output_filename:
        output_filename = os.path.splitext(path)[0] + "-sheet.png"
    out = os.path.abspath(output_filename)
    os.makedirs(os.path.dirname(out), exist_ok=True)

    args = [path, "--sheet", out]
    if columns > 0:
        args += ["--sheet-columns", str(columns)]
    run_command(args)
    return f"Exported sprite sheet {path} -> {out}"


async def run_lua_script(script: str, filename: str = "") -> str:
    """Run an arbitrary Aseprite Lua script (advanced escape hatch).

    If filename is given the sprite is opened first and available as app.sprite.
    The script is responsible for saving any changes (spr:saveAs(spr.filename)).
    Returns whatever the script print()s.
    """
    sprite_path = os.path.abspath(filename) if filename else None
    output = run_script(script, sprite_path=sprite_path)
    return output or "(script produced no output)"
