"""Demo: build a 16x16 slime character with the aseprite-mcp tools.

Produces slime.aseprite, slime.png (8x upscale) and a 2-frame bounce
animation slime.gif in the examples/ directory.

Run: uv run python examples/make_slime.py
"""

import asyncio
import os

from aseprite_mcp.tools import canvas, drawing, export

HERE = os.path.dirname(os.path.abspath(__file__))

PALETTE = {
    "D": "#2e7d32",  # dark green outline
    "G": "#66bb6a",  # body
    "H": "#a5d6a7",  # highlight
    "W": "#ffffff",  # eye white
    "B": "#1b1b1b",  # pupil / mouth
}

# 16x16, '.' = transparent
SLIME = [
    "................",
    "................",
    "......DDDD......",
    "....DDGGGGDD....",
    "...DGGHGGGGGD...",
    "..DGHHGGGGGGGD..",
    "..DGHGGGGGGGGD..",
    ".DGGGGGGGGGGGGD.",
    ".DGGWWGGGGWWGGD.",
    ".DGGWBGGGGWBGGD.",
    ".DGGGGGGGGGGGGD.",
    ".DGGGGGBBGGGGGD.",
    "..DGGGGGGGGGGD..",
    "...DDGGGGGGDD...",
    ".....DDDDDD.....",
    "................",
]

# Squashed pose for the bounce animation
SLIME_SQUASHED = [
    "................",
    "................",
    "................",
    "................",
    "......DDDD......",
    "...DDDGGGGDDD...",
    "..DGGHGGGGGGGD..",
    ".DGHHGGGGGGGGGD.",
    ".DGHGGGGGGGGGGD.",
    "DGGWWGGGGGWWGGGD",
    "DGGWBGGGGGWBGGGD",
    "DGGGGGGBBGGGGGGD",
    ".DGGGGGGGGGGGGD.",
    "..DDGGGGGGGGDD..",
    "....DDDDDDDD....",
    "................",
]


def grid_to_pixels(grid: list[str]) -> list[dict]:
    pixels = []
    for y, row in enumerate(grid):
        assert len(row) == 16, f"row {y} has length {len(row)}"
        for x, ch in enumerate(row):
            if ch != ".":
                pixels.append({"x": x, "y": y, "color": PALETTE[ch]})
    return pixels


async def main() -> None:
    sprite = os.path.join(HERE, "slime.aseprite")

    print(await canvas.create_canvas(16, 16, sprite))
    print(await drawing.draw_pixels(sprite, grid_to_pixels(SLIME), frame=1))

    print(await canvas.add_frame(sprite, duration_ms=150, empty=True))
    print(await drawing.draw_pixels(sprite, grid_to_pixels(SLIME_SQUASHED), frame=2))

    print(await export.export_sprite(sprite, os.path.join(HERE, "slime.png"), scale=8))
    print(await export.export_sprite(sprite, os.path.join(HERE, "slime.gif"), scale=8))
    print(await canvas.get_sprite_info(sprite))


if __name__ == "__main__":
    asyncio.run(main())
