from signal_mcp.formatting import parse_styled_text


def test_no_markers_passthrough():
    assert parse_styled_text("plain text") == ("plain text", [])


def test_bold():
    assert parse_styled_text("**hi**") == ("hi", ["0:2:BOLD"])


def test_strikethrough():
    assert parse_styled_text("~~done~~") == ("done", ["0:4:STRIKETHROUGH"])


def test_monospace():
    assert parse_styled_text("`code`") == ("code", ["0:4:MONOSPACE"])


def test_multiple_markers_offsets():
    text, ranges = parse_styled_text("**Title**\nbody `x=1`")
    assert text == "Title\nbody x=1"
    assert ranges == ["0:5:BOLD", "11:3:MONOSPACE"]


def test_emoji_before_marker_uses_utf16_offset():
    # 🏀 is outside the BMP -> 2 UTF-16 code units, 1 Python codepoint.
    text, ranges = parse_styled_text("🏀 **warmup**")
    assert text == "🏀 warmup"
    # "🏀 " is 2 (surrogate pair) + 1 (space) = 3 UTF-16 units.
    assert ranges == ["3:6:BOLD"]


def test_unmatched_markers_left_literal():
    assert parse_styled_text("no **closing here") == ("no **closing here", [])
