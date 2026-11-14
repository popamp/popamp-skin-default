"""Pictures as SVG: whole rectangles and outlines in colours named by their role.

A role of the metal (METAL) is a class on the element, which a colour set
gives another colour; the display and the lettering (FIXED) stay the same
in every set.
"""
import colorsys
import os

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
FIXED = {
    "lcd": "#06090d",  # the display's ground
    "green": "#52e3a0",  # the display's lettering
    "green-dim": "#1f5a42",
    "grid": "#121c22",
    "ink": "#e6eaf2",  # lettering on buttons and a focused title
    "amber": "#f2a93b",  # thumbs and lamps
    "amber-light": "#edc384",
    "amber-dark": "#9c6214",
    "red": "#f0503c",
}

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
    """skin.toml's [colors] tables: Slate as drawn, the others in their hue."""
    lines = [f"[colors.{FIRST_SET}]", *(f'{role} = "{c}"' for role, c in METAL.items())]
    for name, hue, sat, light in OTHER_SETS:
        lines += ["", f"[colors.{name}]"]
        for role, c in METAL.items():
            _, l, s = colorsys.rgb_to_hls(*(int(c[i : i + 2], 16) / 255 for i in (1, 3, 5)))
            lines.append(f'{role} = "{hexc(colorsys.hls_to_rgb(hue / 360, min(1, light(l)), max(0, min(1, sat(s)))))}"')
    return lines


def colour(role):
    """The fill of a role (or a #rrggbb colour) and its class when a set changes it."""
    if role in METAL:
        return METAL[role], f' class="{role}"'
    return FIXED.get(role, role), ""


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
    return f' class="{role}-{kind}"' if role in METAL else ""
