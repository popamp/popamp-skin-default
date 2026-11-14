"""The bar view's own pictures: a strip of the main window's panel with the display's well along it.

Its buttons are the main window's own sprites, laid out by windows.py.
"""
from parts import well

BAR_H = 22
# The bar's fixed ends (the middle, the title's, is tiled) and the narrowest bar
BAR_LEFT, BAR_RIGHT, BAR_MIN = 315, 223, 640
# The display's well from its left, across the middle into the right end's first WELL_END pixels
DISPLAY_X, WELL_END = 158, 4
WELL_TOP, WELL_H = 1, BAR_H - 2
# The clock's left (its minus sign's place, the digits after it) and its colon
CLOCK = (168, 4)
COLON_X, COLON_ROWS = 36, (4, 9)
# The position bar's whole thumb under the title, on its groove's row
THUMB_TOP, GROOVE_ROW = 10, 5


def display(p, x, w, left=False, right=False):
    """The display's well across `x`..`x + w`, open where it goes on into the next piece: its rim there lies
    past the picture's edge, which cuts it off."""
    well(p, x - (0 if left else 1), WELL_TOP, w + (0 if left else 1) + (0 if right else 1), WELL_H)


def panel(p, w):
    """The bar's panel: flat, without the window's edge, as it lies along the screen's."""
    p.rect(0, 0, w, BAR_H, "body")


def left(p):
    panel(p, BAR_LEFT)
    display(p, DISPLAY_X, BAR_LEFT - DISPLAY_X, left=True)
    cx, cy = CLOCK
    for y in COLON_ROWS:
        p.rect(cx + COLON_X, cy + y, 2, 2, "green")


def mid(p):
    panel(p, 8)
    display(p, 0, 8)
    p.rect(0, THUMB_TOP + GROOVE_ROW - 1, 8, 2, "green-dim")


def right(p):
    panel(p, BAR_RIGHT)
    display(p, 0, WELL_END, right=True)


PICTURES = {"left": (BAR_LEFT, left), "mid": (8, mid), "right": (BAR_RIGHT, right)}
