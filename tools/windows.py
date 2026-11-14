"""The windows skin.toml lays out itself: the main window's bar view and the media library."""
from art_bar import BAR_H, BAR_LEFT, BAR_MIN, BAR_RIGHT, CLOCK, DISPLAY_X, THUMB_TOP
from art_pl import PLATE_W
from parts import BOX


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


TITLE_BUTTON = BOX  # the title bar's buttons: Main Menu at 0, Close at 18, pressed a row down
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
    v, w = "normal", PLATE_W
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
