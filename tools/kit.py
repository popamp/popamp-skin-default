"""Pictures as SVG: whole rectangles and outlines in colours named by their role.

Every role is a class on the element, which a colour set gives another
colour. The tinted sets change only the metal (METAL); the Base16 sets
change the display, the lettering and the lamps (DISPLAY) as well. A
colour written as #rrggbb (the level meters, green to red) is the same in
every set.
"""
import colorsys
import os

from base16 import SCHEMES

# The metal by role, in the first colour set
METAL = {
    "shadow": "#12151c",  # dark edges, the wells' upper rims
    "base": "#262b38",  # the sheets' spare room
    "body": "#2f3545",  # the windows' panel
    "rim": "#3b4358",  # the wells' lower rims, the rules' light line
    "edge": "#666d7f",  # the windows' light edge
    "face-top": "#5d6780",  # a button's face, top to bottom
    "face-bottom": "#394052",
    "face-light": "#8d95a8",  # a button's lit edge
    "sunk-top": "#292f3c",  # a pressed button's face at the top
    "title-top": "#4d6293",  # a focused window's title strip
    "title-bottom": "#2a334b",
    "title-line": "#7b8bb0",
    "title-rule": "#929fbe",
    "dull-top": "#3a3e48",  # an unfocused window's title strip
    "dull-bottom": "#25282f",
    "dull-line": "#6e727b",
    "dull-rule": "#545862",
    "dull-ink": "#868b95",  # an unfocused window's name
    "label": "#acb1ba",  # lettering on the panel
}
DISPLAY = {
    "lcd": "#06090d",  # the display's ground
    "green": "#52e3a0",  # the display's lettering
    "green-dim": "#1f5a42",
    "green-off": "#153629",  # a digit's unlit segments
    "grid": "#121c22",
    "ink": "#e6eaf2",  # lettering on buttons and a focused title
    "amber": "#f2a93b",  # thumbs and lamps
    "amber-light": "#edc384",
    "amber-dark": "#9c6214",
    "red": "#f0503c",
    "select": "#233a6b",  # the picked rows of a list
    "osc-2": "#c1e8de",  # the oscilloscope, from ink at the top to green at the bottom
    "osc-3": "#9ce7c9",
    "osc-4": "#77e5b5",
}
ROLES = {**METAL, **DISPLAY}

FIRST_SET = "Slate"
# (name, hue in degrees, saturation from Slate's, lightness from Slate's)
OTHER_SETS = (
    ("Graphite", 220, lambda s: 0.03, lambda l: l),
    ("Plum", 285, lambda s: s, lambda l: l),
    ("Pine", 165, lambda s: s * 0.9, lambda l: l),
    ("Wine", 345, lambda s: s, lambda l: l),
)


def hexc(rgb):
    return "#%02x%02x%02x" % tuple(round(v * 255) for v in rgb)


def colour_sets():
    """skin.toml's [colors] tables: Slate as drawn, the tinted ones in their hue, then the Base16 ones."""
    lines = [f"[colors.{FIRST_SET}]", *(f'{role} = "{c}"' for role, c in ROLES.items())]
    for name, hue, sat, light in OTHER_SETS:
        lines += ["", f"[colors.{name}]"]
        for role, c in METAL.items():
            _, l, s = colorsys.rgb_to_hls(*(int(c[i : i + 2], 16) / 255 for i in (1, 3, 5)))
            lines.append(f'{role} = "{hexc(colorsys.hls_to_rgb(hue / 360, min(1, light(l)), max(0, min(1, sat(s)))))}"')
    for name, _, _, _, scheme in SCHEMES:
        lines += ["", f'[colors."{name}"]', *(f'{role} = "{c}"' for role, c in base16_set(scheme).items())]
    return lines


def mix(a, b, t):
    """The colour a part `t` of the way from `a` to `b` (#rrggbb)."""
    ca, cb = ([int(c[i : i + 2], 16) for i in (1, 3, 5)] for c in (a, b))
    return "#%02x%02x%02x" % tuple(round(u + (v - u) * t) for u, v in zip(ca, cb))


def luma(c):
    r, g, b = (int(c[i : i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


BLACK = "#000000"
READABLE = 140  # the least luma of lettering on the display (0..255)


def hls(c):
    return colorsys.rgb_to_hls(*(int(c[i : i + 2], 16) / 255 for i in (1, 3, 5)))


def hue_gap(c, hue):
    d = abs(hls(c)[0] * 360 - hue) % 360
    return min(d, 360 - d)


def accent(b, role, hue):
    """The scheme's colour for `role` (base08 red, base0A yellow, base0B green, base0D blue).

    A few schemes put another colour in a role; then the accent nearest the
    role's `hue` (degrees) stands in, if the scheme has one near it.
    """
    if hue_gap(b[role], hue) <= 60:
        return b[role]
    near = min(b[8:], key=lambda c: hue_gap(c, hue))
    return near if hue_gap(near, hue) <= 40 else b[role]


def readable(c, ink):
    """`c`, lightened toward `ink` until lettering in it reads on the dark display."""
    t = 0
    while luma(mix(c, ink, t)) < READABLE and t < 1:
        t += 0.05
    return mix(c, ink, min(t, 1))


def base16_set(b):
    """Every role from a Base16 scheme's sixteen colours (base00..base0F).

    The surfaces go from base00 to base02 (some schemes make base01 the
    darker one, so it is not used), raised parts and edges to base03 and
    base04, the focused title is base0D (blue), the display's lettering
    base0B (green), the thumbs and lamps base0A (yellow) and the
    lettering on buttons the lightest of base05 to base07.
    """
    ground, raised, light = b[0], b[2], b[4]
    ink = max(b[5:8], key=luma)
    lcd = mix(ground, BLACK, 0.55)
    title, green, amber = accent(b, 0xD, 215), readable(accent(b, 0xB, 120), ink), accent(b, 0xA, 45)
    metal = {
        "shadow": mix(ground, BLACK, 0.45),
        "base": ground,
        "body": mix(ground, raised, 0.4),
        "rim": mix(ground, raised, 0.8),
        "edge": mix(raised, light, 0.45),
        "face-top": mix(raised, light, 0.35),
        "face-bottom": mix(ground, raised, 0.9),
        "face-light": mix(b[3], b[5], 0.45),
        "sunk-top": mix(ground, raised, 0.5),
        "title-top": mix(ground, title, 0.5),
        "title-bottom": mix(ground, title, 0.2),
        "title-line": mix(title, b[5], 0.2),
        "title-rule": mix(title, b[5], 0.45),
        "dull-top": mix(ground, raised, 0.7),
        "dull-bottom": mix(ground, raised, 0.25),
        "dull-line": mix(raised, light, 0.4),
        "dull-rule": mix(raised, light, 0.15),
        "dull-ink": mix(b[3], light, 0.5),
        "label": mix(light, b[5], 0.5),
    }
    display = {
        "lcd": lcd,
        "green": green,
        "green-dim": mix(lcd, green, 0.35),
        "green-off": mix(lcd, green, 0.2),
        "grid": mix(lcd, raised, 0.35),
        "ink": ink,
        "amber": amber,
        "amber-light": mix(amber, ink, 0.35),
        "amber-dark": mix(amber, ground, 0.45),
        "red": accent(b, 8, 5),
        "select": mix(ground, title, 0.35),
        **{f"osc-{k}": mix(ink, green, k / 4 - 0.25) for k in (2, 3, 4)},
    }
    return {**metal, **display}


def colour(role):
    """The fill of a role (or a #rrggbb colour) and its class when a set changes it."""
    if role in ROLES:
        return ROLES[role], f' class="{role}"'
    return role, ""


class Gradient:
    """A vertical gradient between two roles, top to bottom."""

    def __init__(self, top, bottom):
        self.top, self.bottom = top, bottom


class Picture:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.defs, self.body, self.ids = [], [], {}

    def paint(self, p):
        if not isinstance(p, Gradient):
            fill, cls = colour(p)
            return f'fill="{fill}"{cls}'
        key = (p.top, p.bottom)
        if key not in self.ids:
            gid = self.ids[key] = f"g{len(self.ids)}"
            stops = [f'<stop offset="{offset}" stop-color="{colour(role)[0]}"{suffixed(role, "stop")}/>' for offset, role in ((0, p.top), (1, p.bottom))]
            self.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">{"".join(stops)}</linearGradient>')
        return f'fill="url(#{self.ids[key]})"'

    def rect(self, x, y, w, h, paint):
        if w > 0 and h > 0:
            self.body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" {self.paint(paint)}/>')

    def path(self, d, paint):
        if d:
            self.body.append(f'<path d="{d}" {self.paint(paint)}/>')

    def line(self, d, role, width=1):
        """A stroked outline, for the few shapes that are lines."""
        self.body.append(f'<path d="{d}" fill="none" stroke="{colour(role)[0]}" stroke-width="{width}"{suffixed(role, "stroke")}/>')

    def svg(self):
        head = f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">'
        defs = f"<defs>\n{chr(10).join(self.defs)}\n</defs>\n" if self.defs else ""
        return f"{head}\n{defs}" + "\n".join(self.body) + "\n</svg>\n"

    def save(self, path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.svg())


def suffixed(role, kind):
    """The class of a role's gradient stop or stroke, which the sets colour as they do its fills."""
    return f' class="{role}-{kind}"' if role in ROLES else ""
