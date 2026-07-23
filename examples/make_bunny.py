"""Demo: 32x32 baby bunny fart animation built with the aseprite-mcp tools.

4 frames: idle -> bracing -> fart! -> cloud dissipates.
Produces bunny.aseprite, per-frame PNGs (8x), bunny.gif and bunny-sheet.png.

Run: uv run python examples/make_bunny.py
"""

import asyncio
import os

from aseprite_mcp.tools import canvas, drawing, export

HERE = os.path.dirname(os.path.abspath(__file__))

OUT = "#5d4037"      # outline brown
FUR = "#fdfdfd"      # white fur
EAR = "#f8bbd0"      # inner ear pink
NOSE = "#f06292"     # nose pink
EYE = "#212121"
BLUSH = "#f9c5d5"
CLOUD1 = "#aed581"   # fart cloud
CLOUD2 = "#c5e1a5"
CLOUD3 = "#dcedc8"
STINK = "#7cb342"    # motion/stink lines


async def draw_bunny(sprite: str, frame: int, *, squat: int = 0, eyes: str = "open",
                     mouth: str = "smile") -> None:
    """Draw the bunny (facing left) on the given frame.

    squat: extra pixels of squash (body/head pushed down, ears splayed).
    eyes: "open" | "shut" | "happy"
    """
    s = squat

    async def ell(x, y, w, h, color, fill=True):
        await drawing.draw_ellipse(sprite, x, y, w, h, color, fill=fill, frame=frame)

    async def px(points):
        await drawing.draw_pixels(sprite, points, frame=frame)

    # ears (drawn first so the head covers their base)
    await ell(6, 1 + s, 5, 12, OUT)
    await ell(12, 1 + s, 5, 12, OUT)
    await ell(7, 2 + s, 3, 10, FUR)
    await ell(13, 2 + s, 3, 10, FUR)
    await px([{"x": 8, "y": yy + s, "color": EAR} for yy in range(4, 9)]
             + [{"x": 14, "y": yy + s, "color": EAR} for yy in range(4, 9)])

    # body + tail
    await ell(13, 13 + s, 16, 14 - s, OUT)
    await ell(14, 14 + s, 14, 12 - s, FUR)
    await ell(24, 15, 6, 6, OUT)
    await ell(25, 16, 4, 4, FUR)

    # head
    await ell(2, 8 + s, 17, 14, OUT)
    await ell(3, 9 + s, 15, 12, FUR)

    # front paw (tucked under the chin)
    await ell(4, 20 + s, 8, 4, OUT)
    await ell(5, 21 + s, 6, 2, FUR)

    # face
    if eyes == "open":
        await px([{"x": 6, "y": 14 + s, "color": EYE}, {"x": 7, "y": 14 + s, "color": EYE},
                  {"x": 6, "y": 15 + s, "color": EYE}, {"x": 7, "y": 15 + s, "color": EYE},
                  {"x": 7, "y": 14 + s, "color": "#ffffff"}])
    elif eyes == "shut":
        await px([{"x": 5, "y": 15 + s, "color": EYE}, {"x": 6, "y": 15 + s, "color": EYE},
                  {"x": 7, "y": 15 + s, "color": EYE}])
    else:  # happy ^_^
        await px([{"x": 5, "y": 15 + s, "color": EYE}, {"x": 6, "y": 14 + s, "color": EYE},
                  {"x": 7, "y": 15 + s, "color": EYE}])

    nose_mouth = [{"x": 3, "y": 16 + s, "color": NOSE}, {"x": 4, "y": 16 + s, "color": NOSE}]
    if mouth == "smile":
        nose_mouth += [{"x": 4, "y": 18 + s, "color": OUT}, {"x": 5, "y": 18 + s, "color": OUT}]
    else:  # effort '>_<'
        nose_mouth += [{"x": 4, "y": 18 + s, "color": OUT}]
    await px(nose_mouth)
    await px([{"x": 5, "y": 17 + s, "color": BLUSH}, {"x": 9, "y": 17 + s, "color": BLUSH}])


async def draw_cloud_small(sprite: str, frame: int) -> None:
    await drawing.draw_ellipse(sprite, 27, 18, 5, 5, CLOUD1, fill=True, frame=frame)
    await drawing.draw_ellipse(sprite, 28, 19, 3, 3, CLOUD2, fill=True, frame=frame)
    await drawing.draw_pixels(sprite, [
        {"x": 25, "y": 19, "color": STINK}, {"x": 26, "y": 21, "color": STINK},
        {"x": 25, "y": 23, "color": STINK},
    ], frame=frame)


async def draw_cloud_big(sprite: str, frame: int) -> None:
    await drawing.draw_ellipse(sprite, 24, 13, 7, 6, CLOUD2, fill=True, frame=frame)
    await drawing.draw_ellipse(sprite, 26, 19, 6, 5, CLOUD2, fill=True, frame=frame)
    await drawing.draw_ellipse(sprite, 25, 15, 4, 3, CLOUD3, fill=True, frame=frame)
    await drawing.draw_ellipse(sprite, 27, 20, 3, 3, CLOUD3, fill=True, frame=frame)
    await drawing.draw_pixels(sprite, [
        {"x": 24, "y": 26, "color": CLOUD3}, {"x": 28, "y": 26, "color": CLOUD3},
        {"x": 26, "y": 11, "color": CLOUD3},
    ], frame=frame)


async def main() -> None:
    sprite = os.path.join(HERE, "bunny.aseprite")

    print(await canvas.create_canvas(32, 32, sprite))

    # frame 1: idle
    await draw_bunny(sprite, 1, eyes="open", mouth="smile")
    # frame 2: bracing (squat, eyes shut)
    await canvas.add_frame(sprite, duration_ms=180, empty=True)
    await draw_bunny(sprite, 2, squat=2, eyes="shut", mouth="effort")
    # frame 3: fart!
    await canvas.add_frame(sprite, duration_ms=140, empty=True)
    await draw_bunny(sprite, 3, squat=1, eyes="shut", mouth="effort")
    await draw_cloud_small(sprite, 3)
    # frame 4: relieved, cloud dissipates
    await canvas.add_frame(sprite, duration_ms=260, empty=True)
    await draw_bunny(sprite, 4, eyes="happy", mouth="smile")
    await draw_cloud_big(sprite, 4)

    # frame 1 duration
    await export.run_lua_script(
        "local s = app.sprite; s.frames[1].duration = 0.35; s:saveAs(s.filename); print('ok')",
        sprite,
    )

    print(await export.export_sprite(sprite, os.path.join(HERE, "bunny.png"), scale=8))
    print(await export.export_sprite(sprite, os.path.join(HERE, "bunny.gif"), scale=8))
    print(await export.export_spritesheet(sprite, os.path.join(HERE, "bunny-sheet.png"), columns=4))
    print(await canvas.get_sprite_info(sprite))


if __name__ == "__main__":
    asyncio.run(main())
