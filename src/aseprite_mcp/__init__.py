"""aseprite-mcp — MCP server that lets AI assistants create 2D pixel-art sprites
by driving the Aseprite CLI in batch mode."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .tools import canvas, drawing, export

mcp = FastMCP(
    "aseprite",
    instructions=(
        "Tools for creating 2D pixel-art sprites with Aseprite. "
        "Typical flow: create_canvas -> draw_* / fill_area -> export_sprite. "
        "Colors are hex strings like #RRGGBB or #RRGGBBAA. "
        "Coordinates are pixels with (0,0) at the top-left. "
        "For animations, use add_frame and pass the frame number to drawing tools, "
        "then export to .gif or use export_spritesheet."
    ),
)

# Canvas management
mcp.tool()(canvas.create_canvas)
mcp.tool()(canvas.add_frame)
mcp.tool()(canvas.add_layer)
mcp.tool()(canvas.get_sprite_info)

# Drawing
mcp.tool()(drawing.draw_pixels)
mcp.tool()(drawing.draw_line)
mcp.tool()(drawing.draw_rectangle)
mcp.tool()(drawing.draw_ellipse)
mcp.tool()(drawing.fill_area)

# Export / advanced
mcp.tool()(export.export_sprite)
mcp.tool()(export.export_spritesheet)
mcp.tool()(export.run_lua_script)


def main() -> None:
    """Entry point: serve MCP over stdio."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
