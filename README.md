# aseprite-mcp — Aseprite로 2D 스프라이트를 만드는 MCP 서버

[Aseprite](https://github.com/aseprite/aseprite)를 배치 모드(CLI + Lua 스크립트)로 조종하는 MCP(Model Context Protocol) 서버입니다.
Claude Code / Claude Desktop에 연결하면 **대화만으로 2D 픽셀 아트 스프라이트를 생성·편집·애니메이션·내보내기** 할 수 있습니다.

```
"32x32 캔버스에 초록색 슬라임 캐릭터를 그리고 PNG로 내보내줘"
"2프레임짜리 점프 애니메이션을 만들어서 GIF로 저장해줘"
```

## 요구 사항

| 항목 | 버전 |
|------|------|
| Python | 3.10 이상 |
| [uv](https://docs.astral.sh/uv/) | 권장 (pip도 가능) |
| Aseprite | v1.2.10 이상 (CLI/Lua 스크립팅 지원 버전) |

### 1. Aseprite 설치

MCP 서버가 실행되는 머신에 Aseprite가 설치되어 있어야 합니다.

- **구매판 (권장)**: [Steam](https://store.steampowered.com/app/431730/Aseprite/) 또는 [aseprite.org](https://www.aseprite.org/)에서 구매 후 설치
- **소스 빌드 (무료)**: 소스는 공개되어 있어 직접 빌드하면 무료로 사용 가능 — [빌드 가이드](https://github.com/aseprite/aseprite/blob/main/INSTALL.md)

설치 후 `aseprite` 명령이 PATH에 없다면 `ASEPRITE_PATH` 환경 변수로 실행 파일 경로를 지정하세요.

| OS | 기본 설치 경로 예시 |
|----|---------------------|
| Windows (Steam) | `C:\Program Files (x86)\Steam\steamapps\common\Aseprite\Aseprite.exe` |
| macOS | `/Applications/Aseprite.app/Contents/MacOS/aseprite` |
| Linux (Steam) | `~/.steam/steam/steamapps/common/Aseprite/aseprite` |

동작 확인:

```bash
aseprite --version        # 또는 "$ASEPRITE_PATH" --version
```

### 2. 서버 설치

```bash
git clone https://github.com/jungrok5/resource-test.git
cd resource-test
uv sync          # 의존성 설치 (또는: pip install -e .)
```

## MCP 등록

### Claude Code

이 저장소에는 `.mcp.json`이 포함되어 있어서 **저장소 폴더에서 Claude Code를 실행하면 자동으로 서버가 연결**됩니다.

다른 프로젝트에서도 쓰려면 전역으로 등록하세요:

```bash
claude mcp add aseprite --scope user \
  --env ASEPRITE_PATH=/path/to/aseprite \
  -- uv run --project /path/to/resource-test aseprite-mcp
```

### Claude Desktop

`claude_desktop_config.json`에 추가:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "uv",
      "args": ["run", "--project", "/path/to/resource-test", "aseprite-mcp"],
      "env": {
        "ASEPRITE_PATH": "/path/to/aseprite"
      }
    }
  }
}
```

등록 후 Claude Code에서는 `/mcp` 명령으로 연결 상태를 확인할 수 있습니다.

## 제공 도구

| 도구 | 설명 |
|------|------|
| `create_canvas` | 새 스프라이트 파일 생성 (너비 × 높이, RGB) |
| `add_frame` | 애니메이션 프레임 추가 (지속 시간 ms 지정) |
| `add_layer` | 레이어 추가 |
| `get_sprite_info` | 크기·프레임·레이어 정보 조회 |
| `draw_pixels` | 픽셀 단위 드로잉 (`[{"x":0,"y":0,"color":"#ff0000"}, ...]`) |
| `draw_line` | 직선 (두께 지정 가능) |
| `draw_rectangle` | 사각형 (외곽선/채우기) |
| `draw_ellipse` | 타원 (외곽선/채우기) |
| `fill_area` | 페인트 버킷(영역 채우기) |
| `export_sprite` | PNG/GIF 등으로 내보내기 (`scale`로 픽셀 아트 확대) |
| `export_spritesheet` | 모든 프레임을 스프라이트 시트 PNG로 내보내기 |
| `run_lua_script` | 임의의 Aseprite Lua 스크립트 실행 (고급) |

- 색상은 `#RRGGBB` 또는 `#RRGGBBAA` 형식의 16진수 문자열
- 좌표는 좌상단이 `(0, 0)`인 픽셀 좌표
- 애니메이션: `add_frame`으로 프레임을 추가하고 드로잉 도구에 `frame` 번호를 넘긴 뒤 `.gif`로 내보내기

## 사용 예시

Claude에게 이렇게 요청해 보세요:

> 16x16 캔버스를 만들고, 빨간 하트 모양을 픽셀로 그린 다음 4배 확대해서 heart.png로 내보내줘

Claude가 내부적으로 수행하는 흐름:

1. `create_canvas(16, 16, "heart.aseprite")`
2. `draw_pixels("heart.aseprite", [{"x":4,"y":3,"color":"#e0245e"}, ...])`
3. `export_sprite("heart.aseprite", "heart.png", scale=4)`

## 개발

```bash
uv run pytest        # Aseprite 없이도 실행 가능한 스모크 테스트
```

## 문제 해결

| 증상 | 해결 |
|------|------|
| `Aseprite executable not found` | Aseprite를 설치하고 `ASEPRITE_PATH`를 실행 파일 전체 경로로 설정 |
| 도구 호출이 멈춤 | Aseprite GUI가 이미 파일을 열고 있는지 확인 (배치 모드와 충돌 가능) |
| GIF에 애니메이션이 없음 | 내보내기 확장자를 `.gif`로 지정했는지 확인 |
