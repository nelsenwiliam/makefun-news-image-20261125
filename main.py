#!/usr/bin/env python3
"""THE WORLD TODAY - Wednesday 25 November 2026.

A procedural newspaper front page summing up the day's world news.
Pure standard library. Deterministic: no randomness, no time, no network.
Writes /output/entry.png (1024x1024 RGB PNG).

Stories (all first reported on 25 Nov 2026):
 1. Zelenskiy confirms Ukraine's drone strike on a Russian cargo ship
    in the Gulf of Finland (Reuters).
 2. Houthi drone hits Riyadh's tallest tower, 11 wounded (Reuters).
 3. CIA and ODNI hit by a cyberattack on classified systems (CNN).
 4. US jury finds Huawei guilty of stealing trade secrets (DoJ / Reuters).
 5. Russian drone briefly enters Polish airspace; NATO sends an AWACS
    radar plane to Poland (Reuters).
Also: Anthropic shares below $83 IPO price; WHO evacuates Ebola staff
in DR Congo; Trump pardons turkeys Freedom and Feathers.
"""
import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 230)
INK = (20, 20, 20)
RED = (178, 58, 44)
DARKRED = (122, 32, 22)
BLUE = (30, 84, 120)
SKY = (205, 226, 238)
NAVY = (24, 52, 76)
STEEL = (52, 73, 94)
GREY = (96, 96, 96)
PALE = (201, 201, 201)
GOLD = (214, 174, 14)
ORANGE = (232, 128, 34)
YELLOW = (243, 198, 16)
GREEN = (40, 176, 96)
DARKGREEN = (18, 90, 52)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CREAM = (240, 226, 190)

# ---------------------------------------------------------------- canvas
px = bytearray(W * H * 3)


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = c


def fill_rect(x, y, w, h, c):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            px[i], px[i + 1], px[i + 2] = c


def rect(x, y, w, h, c, t=1):
    fill_rect(x, y, w, t, c)
    fill_rect(x, y + h - t, w, t, c)
    fill_rect(x, y, t, h, c)
    fill_rect(x + w - t, y, t, h, c)


def hline(x, y, w, c, t=1):
    fill_rect(x, y, w, t, c)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        set_px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                set_px(xx, yy, c)


def ring(cx, cy, r, c, t=2):
    for yy in range(cy - r - t, cy + r + t + 1):
        for xx in range(cx - r - t, cx + r + t + 1):
            d = (xx - cx) ** 2 + (yy - cy) ** 2
            if (r - t) ** 2 <= d <= (r + t) ** 2:
                set_px(xx, yy, c)


def ellipse(cx, cy, rx, ry, c):
    for yy in range(cy - ry, cy + ry + 1):
        for xx in range(cx - rx, cx + rx + 1):
            if ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0:
                set_px(xx, yy, c)


def triangle(p1, p2, p3, c):
    xs = [p1[0], p2[0], p3[0]]
    ys = [p1[1], p2[1], p3[1]]
    for yy in range(min(ys), max(ys) + 1):
        hits = []
        for (ax, ay), (bx, by) in ((p1, p2), (p2, p3), (p3, p1)):
            if ay == by:
                continue
            if min(ay, by) <= yy <= max(ay, by):
                t = (yy - ay) / (by - ay)
                hits.append(ax + t * (bx - ax))
        if len(hits) >= 2:
            for xx in range(int(min(hits)), int(max(hits)) + 1):
                set_px(xx, yy, c)


def polygon(points, c):
    ys = [p[1] for p in points]
    for yy in range(min(ys), max(ys) + 1):
        hits = []
        n = len(points)
        for i in range(n):
            ax, ay = points[i]
            bx, by = points[(i + 1) % n]
            if ay == by:
                continue
            if min(ay, by) <= yy < max(ay, by) or (yy == max(ys) and yy == max(ay, by)):
                t = (yy - ay) / (by - ay)
                hits.append(ax + t * (bx - ax))
        hits.sort()
        for i in range(0, len(hits) - 1, 2):
            for xx in range(int(hits[i]), int(hits[i + 1]) + 1):
                set_px(xx, yy, c)


def starburst(cx, cy, r_out, r_in, spikes, c):
    pts = []
    for i in range(spikes * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi * i / spikes - math.pi / 2
        pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
    polygon(pts, c)


# ---------------------------------------------------------------- 5x7 font
FONT = {
    'A': ("..#..", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '(': ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ')': ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '&': (".###.", "#...#", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '=': (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
}


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, c):
    s = s.upper()
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits[col] == '#':
                    fill_rect(cx + col * scale, y + row * scale, scale, scale, c)
        cx += 6 * scale
    return cx


def draw_text_centered(x, y, w, s, scale, c):
    tw = text_w(s, scale)
    draw_text(x + (w - tw) // 2, y, s, scale, c)


def wrap_text(s, max_w, scale):
    words = s.split(' ')
    lines, cur = [], ''
    for w_ in words:
        trial = (cur + ' ' + w_).strip()
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, s, max_w, scale, c, lh=None):
    if lh is None:
        lh = 7 * scale + 5
    for ln in wrap_text(s, max_w, scale):
        draw_text(x, y, ln, scale, c)
        y += lh
    return y


# ---------------------------------------------------------------- panels
def panel(x, y, w, h):
    fill_rect(x, y, w, h, PAPER)
    rect(x, y, w, h, INK, 3)


def kicker(x, y, s, scale=2):
    draw_text(x, y, s, scale, RED)
    return y + 7 * scale + 4


# ---------------------------------------------------------------- illustrations
def ill_sea(x, y, w, h):
    # dusk sky over the Gulf of Finland, cargo ship hit by drones
    fill_rect(x, y, w, h, SKY)
    sea_y = y + int(h * 0.44)
    fill_rect(x, sea_y, w, h - int(h * 0.44), BLUE)
    # sun low on the horizon, clear of the blast smoke
    circle(x + w - 40, y + 60, 18, GOLD)
    # clouds
    ellipse(x + 60, y + 24, 44, 11, WHITE)
    ellipse(x + 92, y + 20, 28, 9, WHITE)
    ellipse(x + w - 160, y + 40, 38, 10, WHITE)
    # waves
    for wy in (sea_y + 24, sea_y + 58, sea_y + 92, sea_y + 124):
        for wx in range(x + 10, x + w - 10, 34):
            line(wx, wy, wx + 12, wy - 6, (126, 184, 212))
            line(wx + 12, wy - 6, wx + 24, wy, (126, 184, 212))
    # cargo ship (dark silhouette)
    hx, hy = x + 40, sea_y + 28
    polygon([(hx, hy + 24), (hx + 246, hy + 24), (hx + 228, hy + 50),
             (hx + 16, hy + 50)], (44, 62, 80))
    fill_rect(hx + 26, hy, 118, 24, (44, 62, 80))        # deckhouse
    fill_rect(hx + 168, hy + 8, 24, 16, (44, 62, 80))    # funnel
    fill_rect(hx + 60, hy - 18, 60, 18, (44, 62, 80))    # containers
    fill_rect(hx + 126, hy - 18, 60, 18, (74, 92, 110))
    line(hx + 92, hy, hx + 92, hy - 36, (44, 62, 80))     # mast
    fill_rect(hx + 92, hy - 44, 22, 14, RED)             # flag
    for i in range(6):
        circle(hx + 28 + i * 36, hy + 36, 4, (200, 212, 222))
    # explosion above the stern
    ex, ey = x + w - 88, sea_y - 4
    starburst(ex, ey, 56, 25, 9, ORANGE)
    starburst(ex, ey, 38, 17, 9, YELLOW)
    starburst(ex, ey, 20, 9, 8, (255, 242, 182))
    # smoke drifting up
    circle(ex - 54, ey - 44, 19, (118, 118, 118))
    circle(ex - 28, ey - 60, 25, (140, 140, 140))
    circle(ex + 4, ey - 54, 17, (118, 118, 118))
    # two sea drones with dotted approach paths
    for (dx, dy) in ((x + 42, y + 82), (x + 92, y + 56)):
        fill_rect(dx - 8, dy - 3, 16, 6, INK)
        circle(dx - 10, dy - 6, 3, INK)
        circle(dx + 10, dy - 6, 3, INK)
        circle(dx - 10, dy + 6, 3, INK)
        circle(dx + 10, dy + 6, 3, INK)
    for t in range(0, 9):
        fill_rect(x + 108 + t * 12, y + 92 + t * 7, 4, 4, INK)


def ill_tower(x, y, w, h):
    # night over Riyadh: tallest tower, drone strike, smoke
    fill_rect(x, y, w, h, NAVY)
    # stars
    for (sx, sy) in ((x + 30, y + 10), (x + 90, y + 22), (x + 200, y + 8),
                     (x + 280, y + 18), (x + 360, y + 12), (x + 420, y + 24)):
        fill_rect(sx, sy, 3, 3, WHITE)
    # moon
    circle(x + w - 44, y + 16, 12, CREAM)
    circle(x + w - 40, y + 13, 10, NAVY)
    # skyline silhouettes
    for (bx, bw, bh) in ((x, 70, 22), (x + 80, 54, 30), (x + 150, 66, 18),
                          (x + 300, 60, 26), (x + 380, 72, 20)):
        fill_rect(bx, y + h - bh, bw, bh, (16, 36, 54))
    # the tower (tallest, centre-left)
    tx = x + 190
    polygon([(tx, y + h), (tx + 8, y + 14), (tx + 52, y + 14),
             (tx + 60, y + h)], (232, 236, 240))
    polygon([(tx + 8, y + 14), (tx + 52, y + 14), (tx + 46, y + 2),
             (tx + 14, y + 2)], (200, 208, 216))
    # lit windows up the tower
    for wy in range(y + 22, y + h - 8, 14):
        fill_rect(tx + 22, wy, 16, 6, (255, 214, 90))
    # blast at the tower top
    ex, ey = tx + 30, y + 8
    starburst(ex, ey, 30, 14, 8, ORANGE)
    starburst(ex, ey, 19, 9, 8, YELLOW)
    circle(ex - 26, ey - 12, 10, (150, 150, 150))
    circle(ex + 24, ey - 14, 12, (130, 130, 130))
    # small quadcopter drone diving in from the right
    dx, dy = x + w - 74, y + 44
    fill_rect(dx - 10, dy - 3, 20, 6, INK)
    circle(dx - 12, dy - 7, 3, INK)
    circle(dx + 12, dy - 7, 3, INK)
    circle(dx - 12, dy + 7, 3, INK)
    circle(dx + 12, dy + 7, 3, INK)
    for t in range(0, 6):
        fill_rect(dx - 24 - t * 10, dy + 4 + t * 4, 4, 4, (255, 120, 60))


def ill_cyber(x, y, w, h):
    # a shield under attack: breach in the US intelligence agencies
    fill_rect(x, y, w, h, (228, 236, 242))
    # binary rain
    for (bx, by, s) in ((x + 18, y + 8, "01"), (x + 70, y + 16, "10"),
                        (x + 130, y + 6, "01"), (x + 190, y + 14, "11"),
                        (x + 250, y + 8, "01"), (x + 320, y + 16, "10"),
                        (x + 390, y + 6, "01")):
        draw_text(bx, by, s, 1, (140, 160, 175))
    # shield
    cx, cy = x + 120, y + h // 2 + 2
    polygon([(cx - 52, cy - 34), (cx + 52, cy - 34), (cx + 52, cy + 6),
             (cx, cy + 44), (cx - 52, cy + 6)], STEEL)
    polygon([(cx - 44, cy - 27), (cx + 44, cy - 27), (cx + 44, cy + 4),
             (cx, cy + 36), (cx - 44, cy + 4)], (214, 226, 234))
    # crack through the shield
    line(cx - 6, cy - 30, cx + 8, cy - 8, RED)
    line(cx + 8, cy - 8, cx - 4, cy + 10, RED)
    line(cx - 4, cy + 10, cx + 10, cy + 30, RED)
    # padlock on the shield
    lx, ly = cx - 14, cy - 6
    fill_rect(lx, ly, 28, 22, NAVY)
    ring(lx + 14, ly - 2, 10, NAVY, 3)
    fill_rect(lx + 12, ly + 8, 4, 8, GOLD)
    circle(lx + 14, ly + 6, 3, GOLD)
    # red warning triangle with exclamation
    tx, ty = x + w - 96, y + h // 2 - 6
    triangle((tx, ty - 34), (tx + 34, ty + 24), (tx - 34, ty + 24), RED)
    fill_rect(tx - 3, ty - 22, 6, 24, WHITE)
    fill_rect(tx - 3, ty + 8, 6, 6, WHITE)
    draw_text(x + 190, y + h - 22, "CLASSIFIED", 2, DARKRED)


def ill_chip(x, y, w, h):
    # a microchip under a red GUILTY stamp
    fill_rect(x, y, w, h, (240, 238, 228))
    # chip body
    cx, cy = x + 96, y + h // 2
    fill_rect(cx - 44, cy - 34, 88, 68, INK)
    fill_rect(cx - 34, cy - 24, 68, 48, (44, 62, 80))
    fill_rect(cx - 16, cy - 10, 32, 20, GOLD)
    # pins
    for i in range(5):
        fill_rect(cx - 34 + i * 16, cy - 44, 8, 10, INK)
        fill_rect(cx - 34 + i * 16, cy + 34, 8, 10, INK)
        fill_rect(cx - 54, cy - 24 + i * 12, 10, 6, INK)
        fill_rect(cx + 44, cy - 24 + i * 12, 10, 6, INK)
    # circuit traces to the right
    for (ty2, tx2) in ((cy - 20, 96), (cy, 120), (cy + 20, 84)):
        line(cx + 54, ty2, cx + tx2, ty2, (120, 120, 120))
        circle(cx + tx2, ty2, 4, (120, 120, 120))
    # gavel above the chip, left of the stamp
    gx, gy = x + 160, y + 8
    fill_rect(gx, gy, 54, 14, (120, 74, 32))
    fill_rect(gx + 22, gy + 14, 10, 26, (90, 54, 22))
    fill_rect(gx + 6, gy + 40, 42, 8, (120, 74, 32))
    # red GUILTY stamp
    sx, sy = x + 250, y + h - 44
    rect(sx, sy, 172, 32, RED, 4)
    draw_text(sx + 14, sy + 8, "GUILTY", 3, RED)


def ill_radar(x, y, w, h):
    # AWACS radar screen watching the Polish sky
    fill_rect(x, y, w, h, (16, 42, 28))
    cx, cy = x + 110, y + h // 2
    ring(cx, cy, 44, GREEN, 2)
    ring(cx, cy, 30, GREEN, 1)
    ring(cx, cy, 16, GREEN, 1)
    line(cx - 44, cy, cx + 44, cy, DARKGREEN)
    line(cx, cy - 44, cx, cy + 44, DARKGREEN)
    # sweep line
    line(cx, cy, cx + 38, cy - 24, GREEN)
    # blips: one hostile drone, one friendly plane
    circle(cx + 26, cy - 16, 4, RED)
    circle(cx - 20, cy + 18, 4, (120, 255, 170))
    circle(cx + 8, cy + 26, 3, (120, 255, 170))
    # AWACS silhouette at right
    px_, py_ = x + 220, cy
    polygon([(px_, py_ - 5), (px_ + 150, py_ - 5), (px_ + 168, py_),
             (px_ + 150, py_ + 5), (px_, py_ + 5)], (200, 212, 222))
    polygon([(px_ + 46, py_ - 5), (px_ + 84, py_ - 24), (px_ + 108, py_ - 5)],
            (200, 212, 222))
    polygon([(px_ + 46, py_ + 5), (px_ + 84, py_ + 24), (px_ + 108, py_ + 5)],
            (200, 212, 222))
    ellipse(px_ + 92, py_ - 10, 26, 8, (160, 172, 182))


# ---------------------------------------------------------------- build page
def main():
    fill_rect(0, 0, W, H, PAPER)

    # ---- masthead
    draw_text_centered(0, 22, W, "THE WORLD TODAY", 8, INK)
    hline(24, 92, 976, INK, 3)
    hline(24, 98, 976, INK, 1)
    draw_text_centered(0, 106, W, "WEDNESDAY, 25 NOVEMBER 2026", 3, INK)
    draw_text_centered(0, 132, W, "ONE DAY - ONE PAGE - THE WORLD IN BRIEF", 2, GREY)

    # ---- lead story: Gulf of Finland
    lx, ly, lw, lh = 24, 152, 976, 280
    panel(lx, ly, lw, lh)
    ill_sea(lx + 10, ly + 10, 380, lh - 20)
    tx = lx + 406
    tw = lw - 406 - 16
    yy = ly + 16
    yy = kicker(tx, yy, "WAR AT SEA - GULF OF FINLAND", 2)
    for ln in ("KYIV CONFIRMS", "DRONE HIT ON", "RUSSIAN SHIP"):
        draw_text(tx, yy, ln, 4, INK)
        yy += 34
    yy += 8
    draw_para(tx, yy,
              "President Zelenskiy confirmed Ukraine was behind Saturday's "
              "drone strike on a Russian cargo ship in the Gulf of Finland. "
              "Ally Norway urged Kyiv to exercise caution.",
              tw, 2, INK)

    # ---- row 2: two panels
    ry, rh = 442, 232
    # A: Riyadh tower
    ax, aw = 24, 482
    panel(ax, ry, aw, rh)
    ill_tower(ax + 10, ry + 10, aw - 20, 62)
    yy = ry + 84
    yy = kicker(ax + 14, yy, "MIDDLE EAST", 2)
    for ln in ("HOUTHI DRONE HITS", "RIYADH'S TALLEST", "TOWER, 11 HURT"):
        draw_text(ax + 14, yy, ln, 3, INK)
        yy += 26
    yy += 4
    draw_para(ax + 14, yy,
              "Saudi civil defence said 11 people were wounded in the strike.",
              aw - 28, 2, INK)
    # B: CIA / ODNI breach
    bx, bw = 518, 482
    panel(bx, ry, bw, rh)
    ill_cyber(bx + 10, ry + 10, bw - 20, 62)
    yy = ry + 84
    yy = kicker(bx + 14, yy, "CYBERATTACK IN WASHINGTON", 2)
    for ln in ("CIA AND ODNI HIT", "BY CYBER BREACH"):
        draw_text(bx + 14, yy, ln, 3, INK)
        yy += 26
    yy += 4
    draw_para(bx + 14, yy,
              "The breach touched classified information, CNN reported, "
              "citing people familiar with the matter.",
              bw - 28, 2, INK)

    # ---- row 3: two panels
    ty, th = 684, 240
    # C: Huawei verdict
    cx0, cw = 24, 482
    panel(cx0, ty, cw, th)
    ill_chip(cx0 + 10, ty + 10, cw - 20, 56)
    yy = ty + 78
    yy = kicker(cx0 + 14, yy, "US-CHINA TECH", 2)
    for ln in ("HUAWEI GUILTY OF", "STEALING TRADE", "SECRETS"):
        draw_text(cx0 + 14, yy, ln, 3, INK)
        yy += 26
    yy += 4
    draw_para(cx0 + 14, yy,
              "A US jury convicted the Chinese tech giant on 10 of 12 "
              "counts, including bank fraud, after a three-month trial.",
              cw - 28, 2, INK)
    # D: Poland airspace
    dx0, dw = 518, 482
    panel(dx0, ty, dw, th)
    ill_radar(dx0 + 10, ty + 10, dw - 20, 56)
    yy = ty + 78
    yy = kicker(dx0 + 14, yy, "NATO'S EASTERN FLANK", 2)
    for ln in ("RUSSIAN DRONE", "ENTERS POLISH", "AIRSPACE"):
        draw_text(dx0 + 14, yy, ln, 3, INK)
        yy += 26
    yy += 4
    draw_para(dx0 + 14, yy,
              "A Russian drone crossed into Poland during an overnight "
              "attack. NATO is sending a radar plane.",
              dw - 28, 2, INK)

    # ---- footer strip
    fy = 934
    fill_rect(24, fy, 976, 66, INK)
    draw_text(40, fy + 8,
              "ALSO: ANTHROPIC SHARES FALL BELOW $83 IPO PRICE",
              2, WHITE)
    draw_text(40, fy + 27,
              "WHO EVACUATES EBOLA STAFF IN DR CONGO AMID FIGHTING",
              2, WHITE)
    draw_text(40, fy + 46,
              "TRUMP PARDONS TURKEYS FREEDOM AND FEATHERS FOR THANKSGIVING",
              2, (200, 200, 200))

    # ---- write PNG
    out = "/output/entry.png"
    os.makedirs("/output", exist_ok=True)
    write_png(out)


def write_png(path):
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        c += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    prev = bytearray(W * 3)
    for y in range(H):
        row = bytes(px[y * W * 3:(y + 1) * W * 3])
        best = None
        for f in (0, 1, 2):
            if f == 0:
                enc = row
            elif f == 1:
                enc = bytearray(W * 3)
                for i in range(W * 3):
                    left = row[i - 3] if i >= 3 else 0
                    enc[i] = (row[i] - left) & 0xFF
                enc = bytes(enc)
            else:
                enc = bytes((row[i] - prev[i]) & 0xFF for i in range(W * 3))
            score = sum(b if b < 128 else 256 - b for b in enc)
            if best is None or score < best[0]:
                best = (score, f, enc)
        raw.append(best[1])
        raw.extend(best[2])
        prev = bytearray(row)
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", ihdr)
    data += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(data)


if __name__ == "__main__":
    main()
