"""Adds to the skin what the classic sheets do not have: the main window's bar view, the media library's
title and the colour sets.

    python3 -I -B tools/extras.py [skin folder]

The sheets stay as they are drawn; this marks their metal's colours with classes for the colour sets,
writes `bar/` and `ml/` beside them and the part of skin.toml after GENERATED. Running it again gives
the same files.
"""
import colorsys
import os
import re
import sys

# --- colour sets -------------------------------------------------------------------------------------

FIRST_SET = "Slate"
# The metal: blue-greys of this hue, not the near-black display or the near-white lettering
METAL_HUE, METAL_SATURATION, METAL_LIGHTNESS = (214, 226), 0.33, (0.06, 0.9)
# (name, hue in degrees, saturation as a function of the theme's, lightness as a function of the theme's)
OTHER_SETS = (
    ("Graphite", 220, lambda s: 0.03, lambda l: l),
    ("Plum", 285, lambda s: s, lambda l: l),
    ("Pine", 165, lambda s: s * 0.9, lambda l: l),
    ("Wine", 345, lambda s: s, lambda l: l),
)
COLOUR = re.compile(r'\b(fill|stroke|stop-color)="(#[0-9a-fA-F]{6})"')
SUFFIX = {"fill": "", "stroke": "-stroke", "stop-color": "-stop"}


def hls(colour):
    return colorsys.rgb_to_hls(*(int(colour[i : i + 2], 16) / 255 for i in (1, 3, 5)))


def metal_name(colour):
    """The name a colour has in the sets when it is the metal's, else None."""
    h, l, s = hls(colour.lower())
    lo, hi = METAL_LIGHTNESS
    if not (METAL_HUE[0] <= h * 360 <= METAL_HUE[1] and s <= METAL_SATURATION and lo < l < hi):
        return None
    return "metal-" + colour.lower()[1:]


def mark(svg):
    """The SVG with a class on every element painted in the metal's colours, kept where one is already."""

    def tag(m):
        if "class=" in m.group(0):
            return m.group(0)
        classes = [n + SUFFIX[attr] for attr, c in COLOUR.findall(m.group(0)) if (n := metal_name(c))]
        return m.group(0) if not classes else f'{m.group(1)} class="{" ".join(classes)}"{m.group(2)}'

    return re.sub(r"(<\w+)([^>]*>)", tag, svg)


def hexc(rgb):
    return "#%02x%02x%02x" % tuple(round(v * 255) for v in rgb)


def colour_sets(svgs):
    """The [colors] tables for every metal colour in the pictures: the first set as drawn, the others in their hue."""
    metal = sorted({c.lower() for svg in svgs for _, c in COLOUR.findall(svg) if metal_name(c)}, key=lambda c: hls(c)[1])
    lines = [f"[colors.{FIRST_SET}]", *(f'{metal_name(c)} = "{c}"' for c in metal)]
    for name, hue, sat, light in OTHER_SETS:
        lines += ["", f"[colors.{name}]"]
        for c in metal:
            _, l, s = hls(c)
            lines.append(f'{metal_name(c)} = "{hexc(colorsys.hls_to_rgb(hue / 360, min(1, light(l)), max(0, min(1, sat(s)))))}"')
    return lines


# --- pictures ----------------------------------------------------------------------------------------

METAL_TOP, METAL_BOTTOM = "#3b4358", "#262b38"  # the main window's metal, top to bottom
WELL_DARK, WELL_LIGHT, WELL = "#12151c", "#3b4358", "#06090d"  # its display wells: rims and inside
GROOVE, DIGIT = "#153629", "#52e3a0"  # the position bar's groove and the clock's colon
TITLE_INK = {True: "#e6eaf2", False: "#868b95"}  # PLAYLIST on the playlist's title, focused and not


def svg(w, h, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
            f"<defs>\n{defs}</defs>\n{body}</svg>\n")  # fmt: skip


def rect(x, y, w, h, fill):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>\n'


METAL_DEFS = (f'<linearGradient id="metal" x1="0" y1="0" x2="0" y2="1">\n<stop offset="0" stop-color="{METAL_TOP}"/>\n'
              f'<stop offset="1" stop-color="{METAL_BOTTOM}"/>\n</linearGradient>\n')  # fmt: skip

# --- the bar -----------------------------------------------------------------------------------------

BAR_H = 22
# The bar's fixed ends (the middle, the title's, is tiled), and the narrowest bar
BAR_LEFT, BAR_RIGHT, BAR_MIN = 315, 223, 640
# The display's well from its left, across the middle into the right end's first WELL_END pixels
DISPLAY_X, WELL_END = 158, 4
WELL_TOP, WELL_BOTTOM = 1, BAR_H - 2
# The clock's left (its minus sign's place, the digits after it), where the main window has its colon
CLOCK = (168, 4)
COLON_X, COLON_ROWS = 36, (4, 9)
# The position bar's whole thumb under the title, on its groove's row
THUMB_TOP, GROOVE_ROW = 10, 5


def well(x, w, left=False, right=False):
    """The display's well across `x`..`x + w`: dark rim at the top and left, light at the bottom and right."""
    h = WELL_BOTTOM - WELL_TOP + 1
    out = rect(x, WELL_TOP, w, h, WELL_LIGHT) + rect(x, WELL_TOP, w - right, 1, WELL_DARK)
    if left:
        out += rect(x, WELL_TOP, 1, h - 1, WELL_DARK)
    return out + rect(x + left, WELL_TOP + 1, w - left - right, h - 2, WELL)


def bar_left():
    cx, cy = CLOCK
    colon = "".join(rect(cx + COLON_X, cy + y, 2, 2, DIGIT) for y in COLON_ROWS)
    return svg(BAR_LEFT, BAR_H, rect(0, 0, BAR_LEFT, BAR_H, "url(#metal)") + well(DISPLAY_X, BAR_LEFT - DISPLAY_X, left=True) + colon, METAL_DEFS)


def bar_mid():
    return svg(8, BAR_H, rect(0, 0, 8, BAR_H, "url(#metal)") + well(0, 8) + rect(0, THUMB_TOP + GROOVE_ROW, 8, 1, GROOVE), METAL_DEFS)


def bar_right():
    return svg(BAR_RIGHT, BAR_H, rect(0, 0, BAR_RIGHT, BAR_H, "url(#metal)") + well(0, WELL_END, right=True), METAL_DEFS)


# --- the library's title -------------------------------------------------------------------------------

TITLE = "MEDIA LIBRARY"
TITLE_PLATE = (26, 100)  # the playlist's name plate in its sheet: x, width; focused at row 0, not at row 21
TITLE_ROW = 6  # PLAYLIST's letters' top on the plate
CELL_W, CELL_H = 5, 6  # text.svg's letter cells, A to Z along its top row


def font(text_svg):
    """text.svg's letters A to Z, each as its outline's pieces moved to the cell's corner."""
    d = re.search(r'<path d="([^"]*)"', text_svg).group(1)
    letters = {}
    for piece in re.findall(r"M[^M]*", d):
        x, y = (int(v) for v in re.match(r"M(\d+) (\d+)", piece).groups())
        if y < CELL_H:
            letters.setdefault(chr(ord("A") + x // CELL_W), []).append(moved(piece, -(x // CELL_W) * CELL_W, 0))
    return letters


def moved(piece, dx, dy):
    """An outline of M, H and V steps moved by `dx`, `dy`."""
    def step(m):
        op, a, b = m.group(1), int(m.group(2)), m.group(3)
        if op == "M":
            return f"M{a + dx} {int(b) + dy}"
        return f"{op}{a + (dx if op == 'H' else dy)}"

    return re.sub(r"([MHV])(-?\d+)(?: (-?\d+))?", step, piece)


def lettered(letters, text, x, y):
    return "".join(moved(p, x + i * CELL_W, y) for i, ch in enumerate(text) if ch != " " for p in letters[ch])


def title_plate(pledit_svg, letters):
    """The playlist's name plate, both rows, with MEDIA LIBRARY in place of PLAYLIST."""
    px, w = TITLE_PLATE
    # the plate's own drawing: the pledit elements within it, which are its gradient and rims
    plate = [e for e in re.findall(r"<rect [^>]*/>", pledit_svg) if f'x="{px}"' in e and f'width="{w}"' in e]
    grads = set(re.findall(r"url\(#(g\d+)\)", "".join(plate)))
    defs = "".join(re.findall(r'<linearGradient id="(?:%s)".*?</linearGradient>\n' % "|".join(grads), pledit_svg, re.S))
    body = "".join(re.sub(r'x="\d+"', 'x="0"', e) + "\n" for e in plate)
    left = (w - (len(TITLE) * CELL_W - 1)) // 2
    for row, focused in ((0, True), (21, False)):
        body += f'<path d="{lettered(letters, TITLE, left, row + TITLE_ROW)}" fill="{TITLE_INK[focused]}"/>\n'
    return svg(w, 41, body, defs)


# --- skin.toml -----------------------------------------------------------------------------------------

GENERATED = "# --- written by tools/extras.py from here on ---"


def toml(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{k} = {toml(x)}" for k, x in v.items()) + " }"
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(toml(x) for x in v) + "]"
    return f'"{v}"' if isinstance(v, str) else str(v)


def element(kind, place, view="bar", **keys):
    """One element as TOML; a place with a text in it is `edges`, else `rect`."""
    where = "edges" if any(isinstance(v, str) for v in place) else "rect"
    return ["", f"[[window.{view}.element]]", f'type = "{kind}"', f"{where} = {toml(list(place))}",
            *(f"{k} = {toml(v)}" for k, v in keys.items())]  # fmt: skip


def area(sheet, x, y, w, h):
    return {"file": f"{sheet}.svg", "area": [x, y, w, h]}


def end(x):
    """A place in the bar's right end, counted from where that end starts."""
    return f"end-{BAR_RIGHT - x}"


def sprite(sheet, w, h, normal, pressed):
    return {"normal": area(sheet, *normal, w, h), "pressed": area(sheet, *pressed, w, h)}


def toggle(states, w, h, at, flag, click, **more):
    """A shufrep button: `states` are its off, off pressed, on and on pressed corners."""
    x, y = at
    pics = {k: area("shufrep", sx, sy, w, h) for k, (sx, sy) in zip(("normal", "pressed", "on", "on_pressed"), states)}
    return element("toggle", (end(x), y, end(x + w), y + h), **pics, flag=flag, click=click, **more)


TITLE_BUTTON = 9  # the title bar's buttons: Main Menu at 0, Close at 18, pressed a row down
BUTTON_INSET = 3


def bar_window():
    b, mid = TITLE_BUTTON, (BAR_H - TITLE_BUTTON) // 2
    e = ["", "[[window]]", 'key = "main"', "", "[window.bar]", 'edge = "bottom"', f"size = [{BAR_MIN}, {BAR_H}]"]
    e += element("image", (0, 0, BAR_LEFT, BAR_H), normal="bar/left.svg")
    e += element("image", (BAR_LEFT, 0, end(0), BAR_H), normal="bar/mid.svg", fill="tile")
    e += element("image", (end(0), 0, "end", BAR_H), normal="bar/right.svg")
    e += element("button", (BUTTON_INSET, mid, b, b), **sprite("titlebar", b, b, (0, 0), (0, b)),
                 menu_press="main", cursor="mainmenu", tip="Main Menu")  # fmt: skip
    transport = (
        (0, 23, "previous", "Previous", {"shift": "back5s", "ctrl": "start-of-list", "menu": "previous"}),
        (23, 23, "play", "Play", {"shift": "open-file", "ctrl": "open-url", "menu": "play"}),
        (46, 23, "pause", "Pause", {"menu": "pause"}),
        (69, 23, "stop", "Stop", {"shift": "stop-fadeout", "ctrl": "stop-after-current", "menu": "stop"}),
        (92, 22, "next", "Next", {"shift": "fwd5s", "ctrl": "end-of-list", "menu": "next"}),
    )
    for sx, w, click, tip, more in transport:
        e += element("button", (15 + sx, 2, w, 18), **sprite("cbuttons", w, 18, (sx, 0), (sx, 18)), click=click, **more, tip=tip)
    e += element("button", (133, 3, 22, 16), **sprite("cbuttons", 22, 16, (114, 0), (114, 16)),
                 click="open-file", shift="open-folder", ctrl="open-url", menu="eject", tip="Open")  # fmt: skip
    for sx, state in ((0, "playing"), (9, "paused"), (18, "stopped")):
        e += element("image", (DISPLAY_X + 4, mid, 9, 9), normal=area("playpaus", sx, 0, 9, 9), show=state)
    e += element("clock", (*CLOCK, 63, 13), hide="stopped")
    e += element("button", (*CLOCK, 63, 13), press="toggle-time-mode", menu="time")
    e += element("vis", (235, 3, 76, 16))
    e += element("button", (235, 3, 76, 16), press="cycle-vis-mode", menu="vis")
    e += element("marquee", (BAR_LEFT + 3, 3, end(-3), 9), double="file-info", cursor="songname",
                 tip="Song Title (right-click for options)", menu="song-title")  # fmt: skip
    thumb = sprite("posbar", 29, 10, (248, 0), (278, 0))
    e += element("slider", (BAR_LEFT, THUMB_TOP, end(0), THUMB_TOP + 10), value="position", thumb=thumb, thumb_len=29,
                 live=False, show="seekable", cursor="posbar", menu="seek")  # fmt: skip
    track = {"file": "volume.svg", "first": [0, 0, 68, 13], "step": [0, 15], "count": 28}
    thumb = {"normal": area("volume", 15, 422, 14, 11), "pressed": area("volume", 0, 422, 14, 11)}
    thumb = {k: v | {"offset": [0, 1]} for k, v in thumb.items()}
    e += element("slider", (end(9), 4, end(77), 17), value="volume", track=track, thumb=thumb, thumb_len=14, reset=200,
                 wheel_step=8, cursor="volbal", tip="Volume")  # fmt: skip
    eq = ((0, 61), (46, 61), (0, 73), (46, 73))
    e += toggle(eq, 23, 12, (82, 5), "eq-window", "toggle-eq-window")
    e += toggle([(x + 23, y) for x, y in eq], 23, 12, (106, 5), "playlist-window", "toggle-playlist-window")
    rows = (0, 15, 30, 45)
    e += toggle([(28, y) for y in rows], 47, 15, (133, 3), "shuffle", "toggle-shuffle", menu="shuffle")
    e += toggle([(0, y) for y in rows], 28, 15, (180, 3), "repeat", "toggle-repeat", menu="repeat")
    close = BAR_RIGHT - BUTTON_INSET - b
    e += element("button", (end(close), mid, end(close + b), mid + b), **sprite("titlebar", b, b, (18, 0), (18, b)),
                 click="exit", tip="Close")  # fmt: skip
    return e


def library_window():
    """The media library in the playlist's frame, with its own name on the title."""
    pl = lambda x, y, w, h: area("pledit", x, y, w, h)
    focus = lambda x: {"normal": pl(x, 0, 25, 20), "inactive": pl(x, 21, 25, 20)}
    v, (_, w) = "normal", TITLE_PLATE
    e = ["", "[[window]]", 'key = "library"', 'placement = "docked"', 'empty_press = "nothing"', "wheel_scrolls_list = true",
         "", "[window.normal]", "size = [275, 116]", "resize_step = [25, 29]", 'cursor = "pnormal"']  # fmt: skip
    e += element("image", (0, 0, 25, 20), v, **focus(0))
    e += element("image", (25, 0, "end-25", 20), v, **focus(127), fill="tile")
    e += element("image", ("end-25", 0, "end", 20), v, **focus(153))
    title = {"file": "ml/title.svg"}
    e += element("image", (f"center-{w // 2}", 0, f"center+{w - w // 2}", 20), v,
                 normal=title | {"area": [0, 0, w, 20]}, inactive=title | {"area": [0, 21, w, 20]})  # fmt: skip
    e += element("image", (0, 20, 12, "end-38"), v, normal=pl(0, 42, 12, 29), fill="tile")
    e += element("image", ("end-20", 20, "end", "end-38"), v, normal=pl(31, 42, 20, 29), fill="tile")
    e += element("image", (12, "end-38", "end-150", "end"), v, normal=pl(179, 0, 25, 38), fill="tile")
    # the bottom's left end without the Add, Rem, Sel and Misc buttons
    e += element("image", (0, "end-38", 12, "end"), v, normal=pl(0, 72, 12, 38))
    e += element("image", ("end-150", "end-38", "end", "end"), v, normal=pl(126, 72, 150, 38))
    e += element("drag", (0, 0, "end", 20), v, cursor="ptbar")
    e += element("button", ("end-11", 3, "end-2", 12), v, pressed=pl(52, 42, 9, 9), click="toggle-library-window",
                 cursor="pclose", tip="Close")  # fmt: skip
    thumb = {"normal": pl(52, 53, 8, 18), "pressed": pl(61, 53, 8, 18)}
    e += element("library", (12, 20, "end-7", "end-38"), v, menu="library", thumb=thumb)
    e += element("text", ("end-143", "end-28", "end-58", "end-22"), v, text="library-status")
    e += element("text", ("end-82", "end-14", "end-52", "end-8"), v, text="playlist-clock", hide="stopped")
    for x, bw, click in ((5, 8, "previous"), (14, 8, "play"), (23, 8, "pause"), (32, 8, "stop"), (41, 8, "next"), (50, 9, "open-file")):
        e += element("button", (f"end-{150 - x}", "end-16", f"end-{150 - x - bw}", "end-9"), v, click=click)
    e += element("button", ("end-44", "end-29", "end-22", "end-14"), v, menu_release="library", tip="Library Menu")
    e += element("resize", ("end-20", "end-20", "end", "end"), v, cursor="psize")
    return e


# --- the run -------------------------------------------------------------------------------------------


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def build(skin):
    toml_path = os.path.join(skin, "skin.toml")
    sheets = re.findall(r'^\w+ = "([\w.]+\.svg)"$', read(toml_path), re.M)
    letters = font(read(os.path.join(skin, "text.svg")))
    pictures = {
        "bar/left.svg": bar_left(),
        "bar/mid.svg": bar_mid(),
        "bar/right.svg": bar_right(),
        "ml/title.svg": title_plate(read(os.path.join(skin, "pledit.svg")), letters),
    }
    drawn = {name: mark(read(os.path.join(skin, name))) for name in sheets} | {k: mark(v) for k, v in pictures.items()}
    for name, text in drawn.items():
        write(os.path.join(skin, name), text)
    head = read(toml_path).split(GENERATED)[0].rstrip("\n")
    tail = [GENERATED, "", *colour_sets(drawn.values()), *bar_window(), *library_window()]
    write(toml_path, head + "\n\n" + "\n".join(tail) + "\n")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else ".")
