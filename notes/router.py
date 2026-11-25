"""Maze router: find an orthogonal wire route from a point on a bus to a GSU port
that avoids every existing component body, wire and bus.

Units: XML drawing units, lattice of STEP units (default 6).  Output is a list of
(grid-unit) vertices for create_wire().
"""
import re, sys, collections, json

STEP = 6                 # lattice resolution in drawing units
INFLATE = 6              # obstacle margin (drawing units)
XMAX, YMAX = 2600, 3168

S = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()

blocked = set()

def block_rect(x0, y0, x1, y1):
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    for x in range(int(x0 // STEP) * STEP, int(x1) + STEP, STEP):
        for y in range(int(y0 // STEP) * STEP, int(y1) + STEP, STEP):
            if x0 - INFLATE <= x <= x1 + INFLATE and y0 - INFLATE <= y <= y1 + INFLATE:
                blocked.add((x, y))

# component bodies
for m in re.finditer(r'<(User|Gfx)\b[^>]*>', S):
    d = dict(re.findall(r'(\w+)="([^"]*)"', m.group(0)))
    try:
        x, y = int(d['x']), int(d['y'])
        w, h = int(d.get('w', 0)), int(d.get('h', 0))
    except (KeyError, ValueError):
        continue
    if x > 5000 or y > 4000:
        continue
    block_rect(x, y, x + max(w, 2), y + max(h, 2))

# wires and buses
for m in re.finditer(r'<Wire classid="(WireOrthogonal|Bus)"[^>]*>.*?</Wire>', S, re.S):
    blk = m.group(0)
    d = dict(re.findall(r'(\w+)="([^"]*)"', blk[:blk.find('>')]))
    x, y = int(d['x']), int(d['y'])
    pts = [(x + int(a), y + int(b))
           for a, b in re.findall(r'<vertex x="(-?\d+)" y="(-?\d+)"', blk)]
    for p, q in zip(pts, pts[1:]):
        block_rect(p[0], p[1], q[0], q[1])

print('blocked cells', len(blocked))


def free(x, y):
    return (x, y) not in blocked


def neighbours(x, y):
    for dx, dy in ((STEP, 0), (-STEP, 0), (0, STEP), (0, -STEP)):
        nx, ny = x + dx, y + dy
        if 0 <= nx <= XMAX and 0 <= ny <= YMAX and free(nx, ny):
            yield nx, ny


def route(start, goal):
    """BFS from start to goal; both are allowed even if blocked."""
    s = (start[0] // STEP * STEP, start[1] // STEP * STEP)
    g = (goal[0] // STEP * STEP, goal[1] // STEP * STEP)

    def neigh(p):
        out = []
        for dx, dy in ((STEP, 0), (-STEP, 0), (0, STEP), (0, -STEP)):
            n = (p[0] + dx, p[1] + dy)
            if 0 <= n[0] <= XMAX and 0 <= n[1] <= YMAX:
                if n == g or free(*n):
                    out.append(n)
        return out

    prev = {s: None}
    q = collections.deque([s])
    while q:
        cur = q.popleft()
        if cur == g:
            break
        for n in neigh(cur):
            if n not in prev:
                prev[n] = cur
                q.append(n)
    if g not in prev:
        return None
    path = []
    c = g
    while c is not None:
        path.append(c)
        c = prev[c]
    path.reverse()
    return path


def simplify(path):
    if len(path) <= 2:
        return path
    out = [path[0]]
    for i in range(1, len(path) - 1):
        a, b, c = out[-1], path[i], path[i + 1]
        if (b[0] - a[0]) * (c[1] - b[1]) != (b[1] - a[1]) * (c[0] - b[0]):
            out.append(b)
    out.append(path[-1])
    return out


if __name__ == '__main__':
    bx, by, gx, gy = (int(v) for v in sys.argv[1:5])
    p = route((bx, by), (gx, gy))
    print('found' if p else 'NO PATH')
    if p:
        sp = simplify(p)
        print('cells', len(p), 'vertices', len(sp))
        print([(round(x / 18, 2), round(y / 18, 2)) for x, y in sp])
