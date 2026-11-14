"""The parts every window is made of, each drawn here once: the window, its title strip and title buttons,
the wells, the buttons, lamps, thumbs and the lettering.
"""
import os
import re

from kit import Gradient

# --- lettering: text.svg's letters, 5 x 6 cells -------------------------------------------------------

CELL_W, CELL_H = 5, 6
ROWS = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ"@', "0123456789….:()-'!_+\\/[]^&%,=$#")
TEXT_SVG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "text.svg")


def moved(piece, dx, dy):
    """An outline of M, H and V steps moved by `dx`, `dy`."""

    def step(m):
        op, a, b = m.group(1), int(m.group(2)), m.group(3)
        if op == "M":
            return f"M{a + dx} {int(b) + dy}"
        return f"{op}{a + (dx if op == 'H' else dy)}"

    return re.sub(r"([MHV])(-?\d+)(?: (-?\d+))?", step, piece)


def load_font(path=TEXT_SVG):
    """text.svg's letters, each as its outline's pieces moved to the cell's corner."""
    with open(path, encoding="utf-8") as f:
        d = re.search(r'<path d="([^"]*)"', f.read()).group(1)
    letters = {}
    for piece in re.findall(r"M[^M]*", d):
        x, y = (int(v) for v in re.match(r"M(\d+) (\d+)", piece).groups())
        row, col = y // CELL_H, x // CELL_W
        if row < len(ROWS) and col < len(ROWS[row]):
            letters.setdefault(ROWS[row][col], []).append(moved(piece, -col * CELL_W, -row * CELL_H))
    return letters


FONT = load_font()


def text_width(text):
    return len(text) * CELL_W - 1


def letters(p, text, x, y, paint):
    """`text` in the skin's letters, its top left corner at `x`, `y`."""
    p.path("".join(moved(piece, x + i * CELL_W, y) for i, ch in enumerate(text) for piece in FONT.get(ch, ())), paint)


def centred(p, text, x, y, w, paint):
    letters(p, text, x + (w - text_width(text)) // 2, y, paint)


# --- edges and wells ----------------------------------------------------------------------------------


def bevel(p, x, y, w, h, light, dark):
    """A one-pixel edge: `light` along the top and left, `dark` along the bottom and right."""
    p.path(f"M{x} {y}H{x + w}V{y + 1}H{x + 1}V{y + h}H{x}Z", light)
    p.path(f"M{x + w - 1} {y + 1}H{x + w}V{y + h}H{x + 1}V{y + h - 1}H{x + w - 1}Z", dark)


def well(p, x, y, w, h, inside="lcd"):
    """A cut-out in the panel: dark rim at the top and left, light at the bottom and right."""
    bevel(p, x, y, w, h, "shadow", "rim")
    p.rect(x + 1, y + 1, w - 2, h - 2, inside)


def rule(p, x, y, w):
    """A groove across the panel: a dark line over a light one."""
    p.rect(x, y, w, 1, "shadow")
    p.rect(x, y + 1, w, 1, "rim")


def window(p, x, y, w, h):
    """A window's panel and its outer edge."""
    p.rect(x, y, w, h, "body")
    bevel(p, x, y, w, h, "edge", "shadow")


# --- buttons -----------------------------------------------------------------------------------------

RAISED, SUNK = Gradient("face-top", "face-bottom"), Gradient("sunk-top", "face-bottom")


def button(p, x, y, w, h, pressed=False):
    """A button's face; what is on it moves a pixel down and right when it is pressed (see `press`)."""
    p.rect(x, y, w, h, SUNK if pressed else RAISED)
    if pressed:
        bevel(p, x, y, w, h, "shadow", "face-top")
    else:
        bevel(p, x, y, w, h, "face-light", "shadow")


def press(pressed):
    return 1 if pressed else 0


def lamp(p, x, y, on):
    p.rect(x, y, 2, 2, "amber" if on else "shadow")


def lettered_button(p, x, y, w, h, text, pressed=False, lit=None):
    """A button with a word on it, and a lamp at its left when `lit` is not None (on or off)."""
    button(p, x, y, w, h, pressed)
    d = press(pressed)
    top = y + (h - CELL_H) // 2 + d
    ink = "ink" if (lit is None and not pressed) or lit else "label"
    if lit is None:
        centred(p, text, x + d, top, w, ink)
        return
    lamp(p, x + 4 + d, top + 2, lit)
    centred(p, text, x + 7 + d, top, w - 7, ink)


# --- the title strip and its buttons ------------------------------------------------------------------

TITLE_H = 14
BOX = 9  # a title button
STRIP = {True: ("title-top", "title-bottom", "title-line", "title-rule", "ink"), False: ("dull-top", "dull-bottom", "dull-line", "dull-rule", "dull-ink")}
# A title button's glyph as rectangles in its 9 x 9 box
GLYPHS = {
    "menu": ((2, 2, 5, 1), (2, 4, 5, 1), (2, 6, 5, 1)),
    "min": ((2, 5, 5, 2),),
    "shade": ((2, 2, 5, 2),),
    "unshade": ((2, 2, 5, 1), (2, 3, 1, 3), (6, 3, 1, 3), (2, 6, 5, 1)),
}
CLOSE = "M2.5 2.5L6.5 6.5M6.5 2.5L2.5 6.5"


def title_button(p, x, y, glyph, pressed=False):
    button(p, x, y, BOX, BOX, pressed)
    d = press(pressed)
    if glyph == "close":
        p.body.append(f'<g transform="translate({x + d} {y + d})">')
        p.line(CLOSE, "ink", 1.2)
        p.body.append("</g>")
    else:
        p.path("".join(f"M{x + gx + d} {y + gy + d}h{gw}v{gh}h{-gw}z" for gx, gy, gw, gh in GLYPHS[glyph]), "ink")


def strip_ground(p, x, y, w, focused, left=False, right=False):
    """The strip's metal from `x` to `x + w`: lit along the top (and the left end), dark at the bottom (and the right end)."""
    top, bottom, line, _, _ = STRIP[focused]
    p.rect(x, y, w, TITLE_H, Gradient(top, bottom))
    p.rect(x, y, w, 1, line)
    p.rect(x, y + TITLE_H - 1, w, 1, "shadow")
    if left:
        p.rect(x, y, 1, TITLE_H, line)
    if right:
        p.rect(x + w - 1, y, 1, TITLE_H, "shadow")


def title_rules(p, x0, x1, y, focused):
    """The two thin rules either side of a window's name."""
    if x1 > x0:
        rule_ink = STRIP[focused][3]
        p.rect(x0, y + 5, x1 - x0, 1, rule_ink)
        p.rect(x0, y + 8, x1 - x0, 1, rule_ink)


def title_name(p, text, x0, x1, y, focused):
    """A window's name in the middle of `x0`..`x1`, with the rules from the ends up to it."""
    left = x0 + (x1 - x0 - text_width(text)) // 2
    title_rules(p, x0, left - 5, y, focused)
    title_rules(p, left + text_width(text) + 5, x1, y, focused)
    letters(p, text, left, y + 4, STRIP[focused][4])


# Where a window's title buttons are, from its right end; Main Menu from its left
RIGHT_BUTTONS = {"min": 31, "shade": 21, "unshade": 21, "close": 11}
MENU_X = 6
RULES_FROM, RULES_TO = 6, 4  # the rules' margins: from the left end (or after Main Menu), up to the first button


def title_strip(p, x, y, w, name, focused, buttons=("shade", "close"), menu=False):
    """A whole title strip: ground, name, rules and buttons, as every window has it."""
    strip_ground(p, x, y, w, focused, left=True, right=True)
    start = x + (MENU_X + BOX + RULES_FROM - 3 if menu else RULES_FROM)
    first = min((RIGHT_BUTTONS[b] for b in buttons), default=0)
    title_name(p, name, start, x + w - first - RULES_TO, y, focused)
    if menu:
        title_button(p, x + MENU_X, y + 3, "menu")
    for b in buttons:
        title_button(p, x + w - RIGHT_BUTTONS[b], y + 3, b)


# --- thumbs -------------------------------------------------------------------------------------------

AMBER = Gradient("amber-light", "amber-dark")
AMBER_PRESSED = Gradient("amber", "amber-dark")


def thumb(p, x, y, w, h, pressed=False, grip="v"):
    """A slider's amber thumb with a grip line across its middle (`v` upright, `h` lying)."""
    p.rect(x, y, w, h, AMBER_PRESSED if pressed else AMBER)
    bevel(p, x, y, w, h, "amber" if pressed else "amber-light", "amber-dark")
    if grip == "v":
        p.rect(x + w // 2, y + 2, 1, h - 4, "amber-dark")
    else:
        p.rect(x + 2, y + h // 2, w - 4, 1, "amber-dark")


def level_colour(k, n=27):
    """A level's colour from green (0) through amber to red (n)."""
    stops = ((0x52, 0xE3, 0xA0), (0xF2, 0xA9, 0x3B), (0xF0, 0x50, 0x3C))
    t = k / n * 2
    a, b = (stops[0], stops[1]) if t <= 1 else (stops[1], stops[2])
    t = t if t <= 1 else t - 1
    return "#%02x%02x%02x" % tuple(round(u + (v - u) * t) for u, v in zip(a, b))
