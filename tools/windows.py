"""The windows skin.toml lays out itself: the main window's bar view and the media library."""
from art_bar import (BAR_H, BAR_LEFT, BAR_MIN, BAR_RIGHT, BOX, CLOCK, DISPLAY_X, REPEAT, SHUFFLE, THUMB_TOP, TOGGLE_H, VOLUME_H,
                     VOLUME_THUMB, VOLUME_TOP, VOLUME_W)
from art_main import STATES
from art_pl import PLATE_W
import art_ml as ml


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


def toggle(sheet, states, w, h, at, flag, click, **more):
    """A toggle: `states` are its off, off pressed, on and on pressed corners in `sheet`."""
    x, y = at
    pics = {k: area(sheet, sx, sy, w, h) for k, (sx, sy) in zip(("normal", "pressed", "on", "on_pressed"), states)}
    return element("toggle", (end(x), y, end(x + w), y + h), **pics, flag=flag, click=click, **more)


GAP = 3  # between the bar's ends and Main Menu and Close, and between them and their neighbours
TRANSPORT_X = GAP + BOX + GAP
CONTROLS = "bar/controls"


def middle(h):
    """The row that puts something `h` high in the bar's middle."""
    return (BAR_H - h) // 2


def bar_window():
    b, mid = BOX, middle(BOX)
    e = ["", "[[window]]", 'key = "main"', "", "[window.bar]", 'edge = "bottom"', f"size = [{BAR_MIN}, {BAR_H}]"]
    e += element("image", (0, 0, BAR_LEFT, BAR_H), normal="bar/left.svg")
    e += element("image", (BAR_LEFT, 0, end(0), BAR_H), normal="bar/mid.svg", fill="tile")
    e += element("image", (end(0), 0, "end", BAR_H), normal="bar/right.svg")
    e += element("button", (GAP, mid, b, b), **sprite(CONTROLS, b, b, (0, 0), (0, b)),
                 menu_press="main", cursor="mainmenu", tip="Main Menu")  # fmt: skip
    transport = (
        (0, 23, "previous", "Previous", {"shift": "back5s", "ctrl": "start-of-list", "menu": "previous"}),
        (23, 23, "play", "Play", {"shift": "open-file", "ctrl": "open-url", "menu": "play"}),
        (46, 23, "pause", "Pause", {"menu": "pause"}),
        (69, 23, "stop", "Stop", {"shift": "stop-fadeout", "ctrl": "stop-after-current", "menu": "stop"}),
        (92, 22, "next", "Next", {"shift": "fwd5s", "ctrl": "end-of-list", "menu": "next"}),
    )
    for sx, w, click, tip, more in transport:
        e += element("button", (TRANSPORT_X + sx, middle(18), w, 18), **sprite("cbuttons", w, 18, (sx, 0), (sx, 18)), click=click,
                     **more, tip=tip)  # fmt: skip
    e += element("button", (TRANSPORT_X + 114 + GAP, middle(16), 22, 16), **sprite("cbuttons", 22, 16, (114, 0), (114, 16)),
                 click="open-file", shift="open-folder", ctrl="open-url", menu="eject", tip="Open")  # fmt: skip
    for sx, state in ((0, "playing"), (9, "paused"), (18, "stopped")):
        e += element("image", (DISPLAY_X + 4, middle(9), 9, 9), normal=area("playpaus", sx, 0, 9, 9), show=state)
    e += element("clock", (*CLOCK, 63, 13), hide="stopped")
    e += element("button", (*CLOCK, 63, 13), press="toggle-time-mode", menu="time")
    e += element("vis", (BAR_LEFT - 80, middle(16), 76, 16))
    e += element("button", (BAR_LEFT - 80, middle(16), 76, 16), press="cycle-vis-mode", menu="vis")
    e += element("marquee", (BAR_LEFT + 3, 3, end(-3), 9), double="file-info", cursor="songname",
                 tip="Song Title (right-click for options)", menu="song-title")  # fmt: skip
    thumb = sprite("posbar", 29, 10, (248, 0), (278, 0))
    e += element("slider", (BAR_LEFT, THUMB_TOP, end(0), THUMB_TOP + 10), value="position", thumb=thumb, thumb_len=29,
                 live=False, show="seekable", cursor="posbar", menu="seek")  # fmt: skip
    e += volume((end(9), middle(VOLUME_H)))
    eq = ((0, 61), (46, 61), (0, 73), (46, 73))
    e += toggle("shufrep", eq, 23, 12, (82, middle(12)), "eq-window", "toggle-eq-window")
    e += toggle("shufrep", [(x + 23, y) for x, y in eq], 23, 12, (106, middle(12)), "playlist-window", "toggle-playlist-window")
    rows = [TOGGLE_H * i for i in range(len(STATES))]
    (sx, sw), (rx, rw) = SHUFFLE, REPEAT
    e += toggle(CONTROLS, [(sx, y) for y in rows], sw, TOGGLE_H, (133, middle(TOGGLE_H)), "shuffle", "toggle-shuffle", menu="shuffle")
    e += toggle(CONTROLS, [(rx, y) for y in rows], rw, TOGGLE_H, (133 + sw, middle(TOGGLE_H)), "repeat", "toggle-repeat", menu="repeat")
    close = 133 + sw + rw + GAP
    assert close + b + GAP == BAR_RIGHT, "Close sits as far from the bar's end as from Repeat"
    e += element("button", (end(close), mid, end(close + b), mid + b), **sprite(CONTROLS, b, b, (b, 0), (b, b)),
                 click="exit", tip="Close")  # fmt: skip
    return e


def library_window():
    """The media library in the playlist's frame, with its own name on the title and the control strip under it."""
    pl = lambda x, y, w, h: area("pledit", x, y, w, h)
    focus = lambda x: {"normal": pl(x, 0, 25, 20), "inactive": pl(x, 21, 25, 20)}
    v, w = "normal", PLATE_W
    e = ["", "[[window]]", 'key = "library"', 'placement = "docked"', 'empty_press = "nothing"', "wheel_scrolls_list = true",
         "", "[window.normal]", "size = [275, 145]", "resize_step = [25, 29]", 'cursor = "pnormal"']  # fmt: skip
    e += element("image", (0, 0, 25, 20), v, **focus(0))
    e += element("image", (25, 0, "end-25", 20), v, **focus(127), fill="tile")
    e += element("image", ("end-25", 0, "end", 20), v, **focus(153))
    title = {"file": "ml/title.svg"}
    e += element("image", (f"center-{w // 2}", 0, f"center+{w - w // 2}", 20), v,
                 normal=title | {"area": [0, 0, w, 20]}, inactive=title | {"area": [0, 21, w, 20]})  # fmt: skip
    e += strip_pictures(v)
    e += element("image", (0, ml.LIST_TOP, 12, "end-38"), v, normal=pl(0, 42, 12, 29), fill="tile")
    e += element("image", ("end-20", ml.LIST_TOP, "end", "end-38"), v, normal=pl(31, 42, 20, 29), fill="tile")
    e += element("image", (12, "end-38", f"end-{ml.BOTTOM_W}", "end"), v, normal=pl(179, 0, 25, 38), fill="tile")
    # the bottom's left end without the Add, Rem, Sel and Misc buttons
    e += element("image", (0, "end-38", 12, "end"), v, normal=pl(0, 72, 12, 38))
    e += element("image", (f"end-{ml.BOTTOM_W}", "end-38", "end", "end"), v, normal="ml/bottom.svg")
    e += element("drag", (0, 0, "end", ml.STRIP_TOP + ml.DISPLAY_TOP), v, cursor="ptbar")
    e += element("button", ("end-11", 3, "end-2", 12), v, pressed=pl(52, 42, 9, 9), click="toggle-library-window",
                 cursor="pclose", tip="Close")  # fmt: skip
    e += strip_controls(v)
    thumb = {"normal": pl(52, 53, 8, 18), "pressed": pl(61, 53, 8, 18)}
    e += element("library", (12, ml.LIST_TOP, "end-7", "end-38"), v, menu="library", thumb=thumb)
    sx, sy, sw, sh = ml.STATUS
    left, top = ml.BOTTOM_W - sx - 3, ml.BOTTOM - sy - 2
    e += element("text", (f"end-{left}", f"end-{top}", f"end-{left - sw + 6}", f"end-{top - 6}"), v, text="library-status")
    lx, ly, lw, lh = ml.LIST_BUTTON
    e += element("button", (f"end-{ml.BOTTOM_W - lx}", f"end-{ml.BOTTOM - ly}", f"end-{ml.BOTTOM_W - lx - lw}",
                            f"end-{ml.BOTTOM - ly - lh}"), v, menu_release="library", tip="Library Menu")  # fmt: skip
    e += element("resize", ("end-20", "end-20", "end", "end"), v, cursor="psize")
    return e


def strip_pictures(v):
    top, bottom = ml.STRIP_TOP, ml.LIST_TOP
    e = element("image", (0, top, ml.STRIP_LEFT, ml.STRIP_H), v, normal="ml/strip-left.svg")
    e += element("image", (ml.STRIP_LEFT, top, f"end-{ml.STRIP_RIGHT}", bottom), v, normal="ml/strip-mid.svg", fill="tile")
    e += element("image", (f"end-{ml.STRIP_RIGHT}", top, "end", bottom), v, normal="ml/strip-right.svg")
    return e


def strip_controls(v):
    """The strip's controls: the main window's sprites and the bar's volume, on the rows art_ml.py drew for them."""
    display = ml.STRIP_TOP + ml.DISPLAY_TOP
    in_display = lambda h: display + (ml.DISPLAY_H - h) // 2
    e = []
    for sx, state in ((0, "playing"), (9, "paused"), (18, "stopped")):
        e += element("image", (ml.MARGIN + 4, in_display(9), 9, 9), v, normal=area("playpaus", sx, 0, 9, 9), show=state)
    e += element("clock", (*ml.CLOCK, 63, 13), v, hide="stopped")
    e += element("button", (*ml.CLOCK, 63, 13), v, press="toggle-time-mode", menu="time")
    vis_right = ml.RIGHT_MARGIN + 4
    vis = (f"end-{vis_right + 76}", in_display(16), f"end-{vis_right}", in_display(16) + 16)
    e += element("vis", vis, v)
    e += element("button", vis, v, press="cycle-vis-mode", menu="vis")
    e += element("marquee", (ml.CLOCK[0] + 67, in_display(9), f"end-{vis_right + 80}", in_display(9) + 9), v, double="file-info",
                 cursor="songname", tip="Song Title (right-click for options)", menu="song-title")  # fmt: skip
    buttons = ml.STRIP_TOP + ml.BUTTONS_TOP
    transport = (
        (0, 23, "previous", "Previous", {"shift": "back5s", "ctrl": "start-of-list", "menu": "previous"}),
        (23, 23, "play", "Play", {"shift": "open-file", "ctrl": "open-url", "menu": "play"}),
        (46, 23, "pause", "Pause", {"menu": "pause"}),
        (69, 23, "stop", "Stop", {"shift": "stop-fadeout", "ctrl": "stop-after-current", "menu": "stop"}),
        (92, 22, "next", "Next", {"shift": "fwd5s", "ctrl": "end-of-list", "menu": "next"}),
    )
    for sx, bw, click, tip, more in transport:
        e += element("button", (ml.MARGIN + sx, buttons, bw, 18), v, **sprite("cbuttons", bw, 18, (sx, 0), (sx, 18)), click=click,
                     **more, tip=tip)  # fmt: skip
    e += element("button", (ml.MARGIN + 114 + GAP, buttons + 1, 22, 16), v, **sprite("cbuttons", 22, 16, (114, 0), (114, 16)),
                 click="open-file", shift="open-folder", ctrl="open-url", menu="eject", tip="Open")  # fmt: skip
    seek = ml.STRIP_TOP + ml.SEEK_TOP
    e += element("slider", (ml.SEEK_X, seek, f"end-{ml.SEEK_END}", seek + 10), v, value="position",
                 thumb=sprite("posbar", 29, 10, (248, 0), (278, 0)), thumb_len=29, live=False, show="seekable", cursor="posbar",
                 menu="seek")  # fmt: skip
    e += volume((f"end-{vis_right + VOLUME_W}", buttons + (18 - VOLUME_H) // 2), v)
    return e


def volume(at, view="bar"):
    """The bar's volume slider with its left top corner at `at`, counted from the window's end."""
    x, y = at
    right = f"end-{int(x[4:]) - VOLUME_W}"
    track = {"file": f"{CONTROLS}.svg", "first": [0, VOLUME_TOP, VOLUME_W, VOLUME_H], "step": [0, VOLUME_H], "count": 28}
    ty, tw, th = VOLUME_THUMB
    thumb = {"normal": area(CONTROLS, 15, ty, tw, th), "pressed": area(CONTROLS, 0, ty, tw, th)}
    thumb = {k: v | {"offset": [0, (VOLUME_H - th) // 2]} for k, v in thumb.items()}
    return element("slider", (x, y, right, y + VOLUME_H), view, value="volume", track=track, thumb=thumb, thumb_len=tw, reset=200,
                   wheel_step=8, cursor="volbal", tip="Volume")  # fmt: skip
