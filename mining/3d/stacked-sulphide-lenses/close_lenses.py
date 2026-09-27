"""Close lens_*.stl in place: drop each zero-area sliver triangle and split its
neighbour across the long edge at the sliver's middle vertex. No vertex moves,
so the surface and volume are unchanged. Running it again is a no-op."""

import struct
from pathlib import Path

REC = struct.Struct("<12fH")


def degenerate(p, q, r):
    e1 = [q[k] - p[k] for k in range(3)]
    e2 = [r[k] - p[k] for k in range(3)]
    c = (e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0])
    n = lambda v: sum(x * x for x in v) ** 0.5
    return n(c) <= 1e-10 * n(e1) * n(e2)


def close(path):
    data = path.read_bytes()
    count = struct.unpack_from("<I", data, 80)[0]
    recs = [list(REC.unpack_from(data, 84 + 50 * i)) for i in range(count)]
    tris = [[tuple(r[3:6]), tuple(r[6:9]), tuple(r[9:12])] for r in recs]
    owner = {(t[i], t[(i + 1) % 3]): f for f, t in enumerate(tris) for i in range(3)}
    drop, split = set(), {}
    for f, t in enumerate(tris):
        if not degenerate(*t):
            continue
        d2 = lambda a, b: sum((a[k] - b[k]) ** 2 for k in range(3))
        i = max(range(3), key=lambda i: d2(t[i], t[(i + 1) % 3]))
        p, q, m = t[i], t[(i + 1) % 3], t[(i + 2) % 3]
        g = owner[(q, p)]
        n = tris[g]
        d = n[3 - n.index(q) - n.index(p)]
        drop.add(f)
        split[g] = [[q, m, d], [m, p, d]]
    if not drop:
        return 0
    out = []
    for f, r in enumerate(recs):
        if f in drop:
            continue
        for t in split.get(f, [tris[f]]):
            out.append(REC.pack(*r[:3], *t[0], *t[1], *t[2], r[12]))
    path.write_bytes(data[:80] + struct.pack("<I", len(out)) + b"".join(out))
    return len(drop)


if __name__ == "__main__":
    for path in sorted(Path(__file__).parent.glob("lens_*.stl")):
        print(path.name, close(path), "sliver(s) removed")
