"""Helpers for running Aseprite in batch mode with generated Lua scripts."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile


class AsepriteError(Exception):
    """Raised when the Aseprite CLI fails or cannot be found."""


def aseprite_binary() -> str:
    """Return the Aseprite executable path (override with ASEPRITE_PATH)."""
    return os.environ.get("ASEPRITE_PATH", "aseprite")


def ensure_aseprite_available() -> str:
    binary = aseprite_binary()
    resolved = shutil.which(binary) or (binary if os.path.isfile(binary) else None)
    if resolved is None:
        raise AsepriteError(
            f"Aseprite executable not found: '{binary}'. "
            "Install Aseprite and/or set the ASEPRITE_PATH environment variable "
            "to the full path of the executable."
        )
    return resolved


def lua_quote(text: str) -> str:
    """Quote a string for safe embedding in a Lua script."""
    escaped = (
        text.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )
    return f'"{escaped}"'


def parse_color(color: str) -> tuple[int, int, int, int]:
    """Parse '#RGB', '#RRGGBB' or '#RRGGBBAA' into an (r, g, b, a) tuple."""
    value = color.strip().lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    if len(value) == 6:
        value += "ff"
    if len(value) != 8:
        raise ValueError(
            f"Invalid color '{color}'. Use '#RGB', '#RRGGBB' or '#RRGGBBAA'."
        )
    try:
        r, g, b, a = (int(value[i : i + 2], 16) for i in (0, 2, 4, 6))
    except ValueError as exc:
        raise ValueError(
            f"Invalid color '{color}'. Use '#RGB', '#RRGGBB' or '#RRGGBBAA'."
        ) from exc
    return r, g, b, a


def lua_color(color: str) -> str:
    """Return a Lua Color{...} expression for a hex color string."""
    r, g, b, a = parse_color(color)
    return f"Color{{r={r}, g={g}, b={b}, a={a}}}"


def run_command(args: list[str], timeout: int = 120) -> str:
    """Run the Aseprite CLI with the given batch-mode arguments."""
    binary = ensure_aseprite_available()
    cmd = [binary, "-b", *args]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=False
        )
    except subprocess.TimeoutExpired as exc:
        raise AsepriteError(f"Aseprite timed out after {timeout}s: {cmd}") from exc
    if result.returncode != 0:
        raise AsepriteError(
            f"Aseprite exited with code {result.returncode}.\n"
            f"stdout: {result.stdout.strip()}\nstderr: {result.stderr.strip()}"
        )
    return result.stdout.strip()


def run_script(script: str, sprite_path: str | None = None, timeout: int = 120) -> str:
    """Run a Lua script in batch mode, optionally opening a sprite file first.

    When ``sprite_path`` is given the script can access it via ``app.sprite``.
    Returns Aseprite's stdout (anything the script print()s).
    """
    if sprite_path is not None and not os.path.isfile(sprite_path):
        raise AsepriteError(f"Sprite file not found: {sprite_path}")

    with tempfile.NamedTemporaryFile(
        "w", suffix=".lua", delete=False, encoding="utf-8"
    ) as handle:
        handle.write(script)
        script_file = handle.name
    try:
        args: list[str] = []
        if sprite_path is not None:
            args.append(sprite_path)
        args += ["-script", script_file]
        return run_command(args, timeout=timeout)
    finally:
        os.unlink(script_file)
