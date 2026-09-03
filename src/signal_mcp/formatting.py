"""Lightweight markdown -> Signal text-style range conversion.

Signal (via signal-cli's `textStyle` send param) supports rich text as
"start:length:STYLE" ranges over the message body, where start/length are
counted in UTF-16 code units (not Python codepoints — matters for text
containing emoji or other characters outside the Basic Multilingual Plane).

This module lets callers write **bold**, ~~strikethrough~~, and `monospace`
inline in note text; parse_styled_text() strips the markers and returns the
plain text plus the style ranges to pass as the `textStyle` RPC param.
"""

import re

_MARKER_RE = re.compile(r"\*\*(.+?)\*\*|~~(.+?)~~|`(.+?)`", re.DOTALL)
_STYLES = ("BOLD", "STRIKETHROUGH", "MONOSPACE")  # group index -> style name


def _utf16_len(s: str) -> int:
    return len(s.encode("utf-16-le")) // 2


def parse_styled_text(text: str) -> tuple[str, list[str]]:
    """Strip **bold**/~~strike~~/`mono` markers, returning (plain_text, textStyle ranges).

    Markers don't nest; the first-matching marker wins for any given span.
    """
    out: list[str] = []
    ranges: list[str] = []
    cursor = 0
    out_len = 0  # running UTF-16 length of the plain-text output built so far

    for m in _MARKER_RE.finditer(text):
        literal = text[cursor : m.start()]
        out.append(literal)
        out_len += _utf16_len(literal)

        style_idx = next(i for i, g in enumerate(m.groups()) if g is not None)
        inner = m.groups()[style_idx]
        out.append(inner)
        inner_len = _utf16_len(inner)
        ranges.append(f"{out_len}:{inner_len}:{_STYLES[style_idx]}")
        out_len += inner_len
        cursor = m.end()

    out.append(text[cursor:])
    return "".join(out), ranges
