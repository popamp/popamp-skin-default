"""The media library's own pictures: the control strip under its title and its bottom right end.

The strip lies across the window from the title's lower part to the list's top rim. Its upper row is one
display well with the play state, the clock, the song title and the visualizer; its lower row has the
transport and Open buttons, the position bar's groove and the volume. Like the bar view it is a left end, a
tiled middle and a right end, so the wells run on across the pieces. windows.py lays its controls out.
"""
from art_bar import COLON_ROWS, COLON_X
from art_pl import BOTTOM, bottom_ground, grip
from parts import TITLE_H, lettered_button, well

STRIP_TOP, STRIP_H = TITLE_H, 46
LIST_TOP = STRIP_TOP + STRIP_H  # where the list starts, under the strip's last row: the list's top rim
STRIP_LEFT, STRIP_RIGHT, TILE = 160, 90, 8
# Rows inside the strip: the display well, the buttons, the position groove (a well 4 high, the thumb 10 across it)
DISPLAY_TOP, DISPLAY_H = 2, 20
BUTTONS_TOP = 25
GROOVE_TOP, GROOVE_H, SEEK_TOP = 32, 4, 29
# Columns: the display well from MARGIN to the window's end less RIGHT_MARGIN; the groove from SEEK_X to the end less SEEK_END
MARGIN, RIGHT_MARGIN = 11, 6
SEEK_X, SEEK_END = 154, 82
# The clock's corner in the window, as far into the display as the bar's
CLOCK = (MARGIN + 10, STRIP_TOP + DISPLAY_TOP + 3)


def ground(p, w, left=False, right=False):
    """A strip piece's panel, the window's edges at its ends and the list's top rim along its last row."""
    p.rect(0, 0, w, STRIP_H, "body")
    if left:
        p.rect(0, 0, 1, STRIP_H, "edge")
        p.rect(MARGIN, STRIP_H - 1, w - MARGIN, 1, "shadow")
    elif right:
        p.rect(w - 1, 0, 1, STRIP_H, "shadow")
        p.rect(w - 25, STRIP_H - 1, 6, 1, "shadow")
        p.rect(w - 16, STRIP_H - 1, 10, 1, "shadow")
    else:
        p.rect(0, STRIP_H - 1, w, 1, "shadow")


def run(p, x, y, w, h, piece_w, left=False, right=False):
    """A well from `x` across `w` that goes on into the next piece where it is open: its rim there lies past
    the picture's edge, which cuts it off."""
    x0 = x if left else -1
    x1 = x + w if right else piece_w + 1
    well(p, x0, y, x1 - x0, h)


def groove(p, x0, x1, piece_w, left=False, right=False):
    run(p, x0, GROOVE_TOP, x1 - x0, GROOVE_H, piece_w, left, right)
    a, b = (x0 + 1 if left else 0), (x1 - 1 if right else piece_w)
    p.rect(a, GROOVE_TOP + 1, b - a, GROOVE_H - 2, "green-dim")


def strip_left(p):
    w = STRIP_LEFT
    ground(p, w, left=True)
    run(p, MARGIN, DISPLAY_TOP, w - MARGIN, DISPLAY_H, w, left=True)
    cx, cy = CLOCK
    for y in COLON_ROWS:
        p.rect(cx + COLON_X, cy - STRIP_TOP + y, 2, 2, "green")
    groove(p, SEEK_X, w, w, left=True)


def strip_mid(p):
    ground(p, TILE)
    run(p, 0, DISPLAY_TOP, TILE, DISPLAY_H, TILE)
    groove(p, 0, TILE, TILE)


def strip_right(p):
    w = STRIP_RIGHT
    ground(p, w, right=True)
    run(p, 0, DISPLAY_TOP, w - RIGHT_MARGIN, DISPLAY_H, w, right=True)
    groove(p, 0, w - SEEK_END, w, right=True)


# The bottom right end: the status well and the library's menu button, without the playlist's transport
BOTTOM_W = 150
STATUS = (4, 14, 96, 10)  # x, y, w, h in the piece
LIST_BUTTON = (106, 10, 22, 18)


def bottom(p):
    bottom_ground(p, 0, 0, BOTTOM_W, right=True)
    scroll_end = BOTTOM_W - 20 + 4
    p.rect(scroll_end, 0, 1, 1, "shadow")
    p.rect(scroll_end + 1, 0, 8, 1, "rim")
    well(p, *STATUS)
    x, y, w, h = LIST_BUTTON
    lettered_button(p, x, y, w, h, "LIST")
    grip(p, BOTTOM_W - 3, BOTTOM - 3)


PICTURES = {"strip-left": (STRIP_LEFT, STRIP_H, strip_left), "strip-mid": (TILE, STRIP_H, strip_mid),
            "strip-right": (STRIP_RIGHT, STRIP_H, strip_right), "bottom": (BOTTOM_W, BOTTOM, bottom)}  # fmt: skip
