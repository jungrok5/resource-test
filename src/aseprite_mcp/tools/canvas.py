"""Canvas / sprite file management tools."""

from __future__ import annotations

import os

from ..core.commands import lua_quote, run_script


async def create_canvas(width: int, height: int, filename: str = "sprite.aseprite") -> str:
    """Create a new RGB sprite file with the given canvas size."""
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive integers")
    if not filename.endswith((".aseprite", ".ase")):
        filename += ".aseprite"
    path = os.path.abspath(filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    script = f"""
local spr = Sprite({width}, {height}, ColorMode.RGB)
spr:saveAs({lua_quote(path)})
print("created " .. spr.width .. "x" .. spr.height)
"""
    output = run_script(script)
    return f"Canvas created: {path} ({output})"


async def add_frame(filename: str, duration_ms: int = 100) -> str:
    """Append a new animation frame (duplicating the last frame's content)."""
    path = os.path.abspath(filename)
    script = f"""
local spr = app.sprite
local frame = spr:newFrame()
frame.duration = {max(duration_ms, 1)} / 1000
spr:saveAs({lua_quote(path)})
print("frames=" .. #spr.frames)
"""
    output = run_script(script, sprite_path=path)
    return f"Frame added to {path} ({output})"


async def add_layer(filename: str, layer_name: str) -> str:
    """Add a new layer on top of the layer stack."""
    path = os.path.abspath(filename)
    script = f"""
local spr = app.sprite
local layer = spr:newLayer()
layer.name = {lua_quote(layer_name)}
spr:saveAs({lua_quote(path)})
print("layers=" .. #spr.layers)
"""
    output = run_script(script, sprite_path=path)
    return f"Layer '{layer_name}' added to {path} ({output})"


async def get_sprite_info(filename: str) -> str:
    """Report size, color mode, frame count and layer names of a sprite file."""
    path = os.path.abspath(filename)
    script = """
local spr = app.sprite
print("size: " .. spr.width .. "x" .. spr.height)
print("colorMode: " .. tostring(spr.colorMode))
print("frames: " .. #spr.frames)
local names = {}
for i, layer in ipairs(spr.layers) do
  names[i] = layer.name
end
print("layers: " .. table.concat(names, ", "))
"""
    return run_script(script, sprite_path=path)
