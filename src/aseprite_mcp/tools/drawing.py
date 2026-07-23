"""Drawing tools — implemented with app.useTool so cels are managed automatically."""

from __future__ import annotations

import os

from ..core.commands import lua_color, lua_quote, parse_color, run_script


def _use_tool(
    path: str,
    tool: str,
    color: str,
    points: list[tuple[int, int]],
    frame: int,
    thickness: int = 1,
) -> str:
    lua_points = ", ".join(f"Point({x}, {y})" for x, y in points)
    return f"""
local spr = app.sprite
local frame = spr.frames[{frame}]
if frame == nil then error("frame {frame} does not exist") end
app.useTool{{
  tool = {lua_quote(tool)},
  color = {lua_color(color)},
  brush = Brush({max(thickness, 1)}),
  points = {{ {lua_points} }},
  frame = frame,
}}
spr:saveAs({lua_quote(path)})
print("ok")
"""


async def draw_pixels(filename: str, pixels: list[dict], frame: int = 1) -> str:
    """Draw individual pixels. Each pixel is {"x": int, "y": int, "color": "#RRGGBB"}.

    Pixels are grouped by color and drawn with a 1px pencil.
    """
    path = os.path.abspath(filename)
    by_color: dict[str, list[tuple[int, int]]] = {}
    for i, pixel in enumerate(pixels):
        try:
            x, y = int(pixel["x"]), int(pixel["y"])
            color = str(pixel.get("color", "#000000"))
            parse_color(color)
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid pixel at index {i}: {pixel!r} ({exc})") from exc
        by_color.setdefault(color, []).append((x, y))

    if not by_color:
        return "No pixels given; nothing drawn."

    # One useTool call per pixel: passing several points in a single call
    # would connect them with pencil strokes instead of stamping dots.
    chunks = []
    for color, points in by_color.items():
        point_list = ", ".join(f"Point({x}, {y})" for x, y in points)
        chunks.append(
            f"""
local color = {lua_color(color)}
for _, pt in ipairs({{ {point_list} }}) do
  app.useTool{{
    tool = "pencil",
    color = color,
    brush = Brush(1),
    points = {{ pt }},
    frame = frame,
  }}
end"""
        )
    script = f"""
local spr = app.sprite
local frame = spr.frames[{frame}]
if frame == nil then error("frame {frame} does not exist") end
{"".join(chunks)}
spr:saveAs({lua_quote(path)})
print("ok")
"""
    run_script(script, sprite_path=path)
    return f"Drew {sum(len(p) for p in by_color.values())} pixel(s) on frame {frame} of {path}"


async def draw_line(
    filename: str,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    color: str = "#000000",
    thickness: int = 1,
    frame: int = 1,
) -> str:
    """Draw a straight line between two points."""
    path = os.path.abspath(filename)
    script = _use_tool(path, "line", color, [(x1, y1), (x2, y2)], frame, thickness)
    run_script(script, sprite_path=path)
    return f"Line ({x1},{y1})-({x2},{y2}) drawn on frame {frame} of {path}"


async def draw_rectangle(
    filename: str,
    x: int,
    y: int,
    width: int,
    height: int,
    color: str = "#000000",
    fill: bool = False,
    frame: int = 1,
) -> str:
    """Draw a rectangle (outline by default, filled when fill=true)."""
    path = os.path.abspath(filename)
    tool = "filled_rectangle" if fill else "rectangle"
    points = [(x, y), (x + width - 1, y + height - 1)]
    script = _use_tool(path, tool, color, points, frame)
    run_script(script, sprite_path=path)
    return f"{'Filled' if fill else 'Outlined'} rectangle {width}x{height} at ({x},{y}) drawn on frame {frame} of {path}"


async def draw_ellipse(
    filename: str,
    x: int,
    y: int,
    width: int,
    height: int,
    color: str = "#000000",
    fill: bool = False,
    frame: int = 1,
) -> str:
    """Draw an ellipse inside the bounding box (x, y, width, height)."""
    path = os.path.abspath(filename)
    tool = "filled_ellipse" if fill else "ellipse"
    points = [(x, y), (x + width - 1, y + height - 1)]
    script = _use_tool(path, tool, color, points, frame)
    run_script(script, sprite_path=path)
    return f"{'Filled' if fill else 'Outlined'} ellipse {width}x{height} at ({x},{y}) drawn on frame {frame} of {path}"


async def fill_area(
    filename: str, x: int, y: int, color: str = "#000000", frame: int = 1
) -> str:
    """Flood-fill (paint bucket) starting from the given point."""
    path = os.path.abspath(filename)
    script = _use_tool(path, "paint_bucket", color, [(x, y)], frame)
    run_script(script, sprite_path=path)
    return f"Flood fill at ({x},{y}) with {color} on frame {frame} of {path}"
