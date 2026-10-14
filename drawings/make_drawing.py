"""Workshop drawing of the oak table: three orthographic views with mm dimensions.

Run:  python3 drawings/make_drawing.py [en|ru]
Output: drawings/table_drawing.svg (English) or drawings/table_drawing_ru.svg (Russian);
A3 landscape, scale 1:10, first-angle projection.

Model axes (mm): X along the length, Y across the width, Z up, origin at floor centre.
Dimensions match build_table.py.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LANG = sys.argv[1] if len(sys.argv) > 1 else "en"
OUT = os.path.join(HERE, "table_drawing.svg" if LANG == "en" else f"table_drawing_{LANG}.svg")

STRINGS = {
    "en": dict(
        front="FRONT VIEW", side="SIDE VIEW",
        top="TOP VIEW (frame, slats and stretcher hidden under the top)",
        span="1200 (slats, stretcher)",
        parts=[("Tabletop", "glued oak boards"),
               ("Leg post", "floor to underside of top"),
               ("Frame rail", "between posts, top + bottom"),
               ("Upper slat", "laid flat under the top"),
               ("Floor stretcher", "laid flat, centred")],
        cols=[(0, "Pos"), (9, "Part"), (36, "Qty"), (45, "Length"), (59, "Width"), (72, "Thick."), (85, "Notes")],
        notes=[
            "NOTES",
            "1. All dimensions in mm. Finished (net) sizes, square butt joints.",
            "   Add tenon/dowel length to parts 3, 4, 5 if mortise-and-tenon is used.",
            "2. Material: solid oak. All frame parts from 90 x 45 section;",
            "   the 90 side of parts 2 and 3 runs along the table length.",
            "3. Leg frames are 210 in from each end, 60 in from each long edge.",
            "4. Upper slats are flush with the top of the frame rails (fixed to the",
            "   underside of the top); stretcher sits on the floor, flush with the",
            "   bottom rails. Ease all edges ~R3. Oil finish.",
        ],
        title="OAK DINING TABLE 1800 x 900 x 790",
        material="Material: solid oak, 90 x 45 frame stock",
        projection="Projection: first angle", units="Units: mm",
        scale="Scale 1:10", sheet="Sheet A3",
    ),
    "ru": dict(
        front="ВИД СПЕРЕДИ", side="ВИД СБОКУ",
        top="ВИД СВЕРХУ (рамы, планки и стяжка скрыты под столешницей)",
        span="1200 (планки, стяжка)",
        parts=[("Столешница", "клеёный щит из дуба"),
               ("Стойка ножки", "от пола до столешницы"),
               ("Перекладина рамы", "между стойками, верх + низ"),
               ("Верхняя планка", "плашмя под столешницей"),
               ("Нижняя стяжка", "плашмя, по центру")],
        cols=[(0, "Поз."), (10, "Наименование"), (43, "Кол."), (52, "Длина"), (65, "Ширина"), (80, "Толщ."), (93, "Примечание")],
        notes=[
            "ПРИМЕЧАНИЯ",
            "1. Все размеры в мм. Чистовые размеры, соединения встык.",
            "   При соединении на шипах добавить длину шипа к поз. 3, 4, 5.",
            "2. Материал: массив дуба. Все детали рам из бруса 90 x 45;",
            "   сторона 90 у поз. 2 и 3 направлена вдоль стола.",
            "3. Рамы отстоят на 210 от торцов и на 60 от длинных кромок.",
            "4. Верхние планки заподлицо с верхними перекладинами (крепятся",
            "   к столешнице снизу); стяжка лежит на полу заподлицо с нижними",
            "   перекладинами. Притупить кромки ~R3. Покрытие маслом.",
        ],
        title="СТОЛ ОБЕДЕННЫЙ ИЗ ДУБА 1800 x 900 x 790",
        material="Материал: массив дуба, брус рам 90 x 45",
        projection="Проецирование: метод E (ЕСКД)", units="Размеры: мм",
        scale="Масштаб 1:10", sheet="Формат А3",
    ),
}
TX = STRINGS[LANG]

# --- table geometry (mm) -----------------------------------------------------
L, W, H, T = 1800, 900, 790, 45          # overall length, width, height; top thickness
S = 45                                   # stock thickness (90x45 everywhere)
M = 90                                   # stock width
FH = H - T                               # frame height 745
FX0, FX1 = L / 2 - 210 - M, L / 2 - 210  # frame X extents (+ side): 600..690
FY = W / 2 - 60                          # frame half width 390
AY0, AY1 = 200 - M / 2, 200 + M / 2      # upper slat Y extents (+ side): 155..245
INNER = FX0                              # slats / stretcher run between frames: -600..600

SCALE = 0.1                              # 1:10
SHEET_W, SHEET_H = 420, 297

# paper origins of the views (paper mm)
FRONT = dict(ox=55 + L / 2 * SCALE, oy=130)              # model (x, z) -> paper
SIDE = dict(ox=330, oy=130)                              # model (y, z)
TOP = dict(ox=FRONT["ox"], oy=212)                       # model (x, y)

svg = []


def P(view, a, b):
    """Model coords to paper coords for a view; b is up (z) or across (y)."""
    if view is TOP:
        return view["ox"] + a * SCALE, view["oy"] + b * SCALE   # +Y (far side) down
    return view["ox"] + a * SCALE, view["oy"] - b * SCALE


def line(x1, y1, x2, y2, cls):
    svg.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" class="{cls}"/>')


def rect(view, a0, b0, a1, b1, cls="vis"):
    (x0, y0), (x1, y1) = P(view, a0, b0), P(view, a1, b1)
    svg.append(f'<rect x="{min(x0, x1):.2f}" y="{min(y0, y1):.2f}" width="{abs(x1 - x0):.2f}" '
               f'height="{abs(y1 - y0):.2f}" class="{cls}"/>')


def mline(view, a0, b0, a1, b1, cls):
    line(*P(view, a0, b0), *P(view, a1, b1), cls)


def text(x, y, s, size=3.5, anchor="middle", rot=0, cls="txt"):
    tr = f' transform="rotate({rot} {x:.2f} {y:.2f})"' if rot else ""
    svg.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" text-anchor="{anchor}" '
               f'class="{cls}"{tr}>{s}</text>')


def arrow(x, y, dx, dy):
    """Filled arrowhead with tip at (x, y) pointing along (dx, dy)."""
    n = (dx * dx + dy * dy) ** 0.5
    ux, uy = dx / n, dy / n
    bx, by = x - ux * 2.5, y - uy * 2.5
    px, py = -uy * 0.6, ux * 0.6
    svg.append(f'<path d="M{x:.2f},{y:.2f} L{bx + px:.2f},{by + py:.2f} '
               f'L{bx - px:.2f},{by - py:.2f} Z" class="arr"/>')


def hdim(view, a0, a1, b_ref0, b_ref1, off, label=None):
    """Horizontal dimension between model positions a0..a1; extension lines start at
    the feature heights b_ref0/b_ref1; the dimension line sits `off` paper-mm away
    (negative = above)."""
    x0, y0 = P(view, a0, b_ref0)
    x1, y1 = P(view, a1, b_ref1)
    yd = (min(y0, y1) if off < 0 else max(y0, y1)) + off
    for x, y in ((x0, y0), (x1, y1)):
        line(x, y + (-1 if off < 0 else 1), x, yd + (-1.5 if off < 0 else 1.5), "dim")
    line(x0, yd, x1, yd, "dim")
    label = label or f"{abs(a1 - a0):g}"
    if abs(x1 - x0) < 7:                       # tight: arrows outside, text beside
        arrow(x0, yd, 1, 0); arrow(x1, yd, -1, 0)
        line(x0 - 4, yd, x0, yd, "dim"); line(x1, yd, x1 + 4, yd, "dim")
        text((x0 + x1) / 2, yd - 1.2, label, size=3)
    else:
        arrow(x0, yd, -1, 0); arrow(x1, yd, 1, 0)
        text((x0 + x1) / 2, yd - 1.2, label)


def vdim(view, b0, b1, a_ref0, a_ref1, off, label=None):
    """Vertical dimension between model positions b0..b1 (paper y)."""
    x0, y0 = P(view, a_ref0, b0)
    x1, y1 = P(view, a_ref1, b1)
    xd = (min(x0, x1) if off < 0 else max(x0, x1)) + off
    for x, y in ((x0, y0), (x1, y1)):
        line(x + (-1 if off < 0 else 1), y, xd + (-1.5 if off < 0 else 1.5), y, "dim")
    line(xd, y0, xd, y1, "dim")
    label = label or f"{abs(b1 - b0):g}"
    if abs(y1 - y0) < 7:
        top, bot = min(y0, y1), max(y0, y1)
        arrow(xd, top, 0, 1); arrow(xd, bot, 0, -1)
        line(xd, top - 4, xd, top, "dim"); line(xd, bot, xd, bot + 4, "dim")
        text(xd + 1.5, (y0 + y1) / 2 + 1.1, label, size=3, anchor="start")
    else:
        arrow(xd, min(y0, y1), 0, -1); arrow(xd, max(y0, y1), 0, 1)
        text(xd - 1.2, (y0 + y1) / 2, label, rot=-90)


def balloon(x, y, tx, ty, n):
    """Part number in a circle at (x, y) with a leader to the point (tx, ty)."""
    dx, dy = tx - x, ty - y
    d = (dx * dx + dy * dy) ** 0.5
    line(x + dx / d * 3.5, y + dy / d * 3.5, tx, ty, "thin")
    svg.append(f'<circle cx="{tx:.2f}" cy="{ty:.2f}" r="0.6" class="arr"/>')
    svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.5" class="vis"/>')
    text(x, y + 1.3, str(n), size=3.5)


def view_title(view_xy, s):
    x, y = view_xy
    text(x, y, s, size=4, cls="ttl")


# --- front view (looking at the long side) ----------------------------------
F = FRONT
rect(F, -L / 2, FH, L / 2, H)                                    # 1 tabletop
for sx in (-1, 1):
    rect(F, sx * FX0, 0, sx * FX1, FH)                           # leg frame (post face)
rect(F, -INNER, FH - S, INNER, FH)                               # 4 upper slats
rect(F, -INNER, 0, INNER, S)                                     # 5 floor stretcher
mline(F, 0, -6, 0, H + 6, "ctr")
line(F["ox"] - L / 2 * SCALE - 8, F["oy"], F["ox"] + L / 2 * SCALE + 8, F["oy"], "thin")

hdim(F, -L / 2, L / 2, H, H, -9)                                 # 1800
for a0, a1 in ((-L / 2, -FX1), (-FX1, -FX0), (-FX0, FX0), (FX0, FX1), (FX1, L / 2)):
    hdim(F, a0, a1, 0, 0, 9)                                     # 210 90 1200 90 210
for b0, b1 in ((0, S), (S, FH - S), (FH - S, FH), (FH, H)):
    vdim(F, b0, b1, L / 2, L / 2, 8)                             # 45 655 45 45
vdim(F, 0, H, -L / 2, -L / 2, -9)                                # 790
vdim(F, 0, FH, -L / 2, -L / 2, -18)                              # 745

x, y = P(F, -300, FH - S / 2); balloon(x - 6, y + 18, x, y, 4)
x, y = P(F, 300, S / 2); balloon(x + 6, y - 18, x, y, 5)
x, y = P(F, FX0 + M / 2, 350); balloon(x - 16, y, x, y, 2)
x, y = P(F, 790, H - T / 2); balloon(x, y + 16, x, y, 1)
view_title((F["ox"], F["oy"] - H * SCALE - 20), TX["front"])

# --- side view (looking at the end, from the left in first angle) ------------
V = SIDE
rect(V, -W / 2, FH, W / 2, H)                                    # tabletop
for sy in (-1, 1):
    rect(V, sy * (FY - S), 0, sy * FY, FH)                       # 2 posts, full height
rect(V, -(FY - S), FH - S, FY - S, FH)                           # 3 top rail
rect(V, -(FY - S), 0, FY - S, S)                                 # 3 bottom rail
for sy in (-1, 1):                                               # hidden: slat ends
    for a in (AY0, AY1):
        mline(V, sy * a, FH - S, sy * a, FH, "hid")
    mline(V, sy * M / 2, 0, sy * M / 2, S, "hid")                # hidden: stretcher end
mline(V, 0, -6, 0, H + 6, "ctr")
line(V["ox"] - W / 2 * SCALE - 8, V["oy"], V["ox"] + W / 2 * SCALE + 8, V["oy"], "thin")

hdim(V, -W / 2, W / 2, H, H, -9)                                 # 900
for a0, a1 in ((-W / 2, -FY), (-FY, -(FY - S)), (-(FY - S), FY - S), (FY - S, FY), (FY, W / 2)):
    hdim(V, a0, a1, 0, 0, 9)                                     # 60 45 690 45 60
hdim(V, -FY, FY, 0, 0, 19)                                       # 780
x, y = P(V, 100, FH - S / 2); balloon(x + 8, y + 16, x, y, 3)
x, y = P(V, -FY + S / 2, 350); balloon(x - 14, y, x, y, 2)
view_title((V["ox"], V["oy"] - H * SCALE - 20), TX["side"])

# --- top view (looking down; everything under the top is hidden) --------------
Tv = TOP
rect(Tv, -L / 2, -W / 2, L / 2, W / 2)
for sx in (-1, 1):
    rect(Tv, sx * FX0, -FY, sx * FX1, FY, "hid")                 # frame footprint
    for sy in (-1, 1):
        mline(Tv, sx * FX0, sy * (FY - S), sx * FX1, sy * (FY - S), "hid")
for sy in (-1, 1):
    rect(Tv, -INNER, sy * AY0, INNER, sy * AY1, "hid")           # 4 upper slats
rect(Tv, -INNER, -M / 2, INNER, M / 2, "hid")                    # 5 stretcher
mline(Tv, 0, -W / 2 - 30, 0, W / 2 + 30, "ctr")
mline(Tv, -L / 2 - 60, 0, L / 2 + 60, 0, "ctr")

ys = [-W / 2, -AY1, -AY0, -M / 2, M / 2, AY0, AY1, W / 2]
for b0, b1 in zip(ys, ys[1:]):
    vdim(Tv, b0, b1, L / 2, L / 2, 8)                            # 205 90 110 90 110 90 205
vdim(Tv, -W / 2, W / 2, -L / 2, -L / 2, -9)                      # 900
hdim(Tv, -L / 2, L / 2, W / 2, W / 2, 9)                         # 1800
hdim(Tv, -INNER, INNER, W / 2, W / 2, 18, TX["span"])
view_title((Tv["ox"], Tv["oy"] - W / 2 * SCALE - 6), TX["top"])

# --- parts list -----------------------------------------------------------------
sizes = [(1, "1800", "900"), (4, "745", "90"), (4, "690", "90"), (2, "1200", "90"), (1, "1200", "90")]
parts = [(str(n), name, qty, length, width, "45", note)
         for n, ((name, note), (qty, length, width)) in enumerate(zip(TX["parts"], sizes), start=1)]
cols = TX["cols"]
tx0, ty0, rh, tw = 254, 160, 6.5, 153
svg.append(f'<rect x="{tx0}" y="{ty0}" width="{tw}" height="{rh * (len(parts) + 1)}" class="vis"/>')
for i in range(1, len(parts) + 1):
    line(tx0, ty0 + rh * i, tx0 + tw, ty0 + rh * i, "thin")
for cx, _ in cols[1:]:
    line(tx0 + cx, ty0, tx0 + cx, ty0 + rh * (len(parts) + 1), "thin")
for cx, name in cols:
    text(tx0 + cx + 1.5, ty0 + 4.6, name, size=3.2, anchor="start", cls="ttl")
for r, row in enumerate(parts, start=1):
    for (cx, _), val in zip(cols, row):
        text(tx0 + cx + 1.5, ty0 + rh * r + 4.6, str(val), size=3.2, anchor="start")

notes = TX["notes"]
for i, s in enumerate(notes):
    text(254, 211 + i * 4.6, s, size=3.1, anchor="start", cls="ttl" if i == 0 else "txt")

# --- frame and title block -----------------------------------------------------------
svg.append(f'<rect x="10" y="10" width="{SHEET_W - 20}" height="{SHEET_H - 20}" class="border"/>')
bx, by, bw, bh = 254, 258, 156, 29
svg.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" class="vis"/>')
line(bx, by + 13, bx + bw, by + 13, "thin")
line(bx + 105, by + 13, bx + 105, by + bh, "thin")
text(bx + bw / 2, by + 9, TX["title"], size=5.2, cls="ttl")
text(bx + 3, by + 20, TX["material"], size=3.2, anchor="start")
text(bx + 3, by + 25.5, TX["projection"], size=3.2, anchor="start")
text(bx + 72, by + 25.5, TX["units"], size=3.2, anchor="start")
text(bx + 130.5, by + 20, TX["scale"], size=3.5, cls="ttl")
text(bx + 130.5, by + 25.5, TX["sheet"], size=3.2)

style = """
<style>
  .vis { fill: none; stroke: #000; stroke-width: 0.5; }
  .hid { fill: none; stroke: #000; stroke-width: 0.25; stroke-dasharray: 2.5 1.2; }
  .ctr { stroke: #000; stroke-width: 0.18; stroke-dasharray: 8 1.2 1.2 1.2; }
  .dim, .thin { stroke: #000; stroke-width: 0.18; }
  .arr { fill: #000; stroke: none; }
  .border { fill: none; stroke: #000; stroke-width: 0.7; }
  text { font-family: 'Helvetica Neue', Arial, sans-serif; fill: #000; }
  .ttl { font-weight: 600; }
</style>"""

doc = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{SHEET_W}mm" height="{SHEET_H}mm" '
       f'viewBox="0 0 {SHEET_W} {SHEET_H}">{style}\n'
       f'<rect width="{SHEET_W}" height="{SHEET_H}" fill="#fff"/>\n' + "\n".join(svg) + "\n</svg>\n")
with open(OUT, "w") as f:
    f.write(doc)
print("Saved", OUT)
