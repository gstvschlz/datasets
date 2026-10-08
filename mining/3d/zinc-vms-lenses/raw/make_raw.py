"""Copy the clean drill-hole tables into raw/ with planted data-entry errors.

Run from anywhere with Python 3.8+: ``python make_raw.py``. Prints where each error landed.
"""

import csv
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
rng = random.Random(20260926)


def read(name):
    with open(HERE.parent / name, newline="") as f:
        rows = list(csv.reader(f))
    return rows[0], rows[1:]


def write(name, header, rows):
    with open(HERE / name, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def of(rows, hole):
    return [r for r in rows if r[0] == hole]


def jitter(value, rel):
    decimals = len(value.split(".")[1]) if "." in value else 0
    return f"{float(value) * (1 + rng.uniform(-rel, rel)):.{decimals}f}"


tables = {n: read(n + ".csv") for n in ("collars", "surveys", "assays", "lithology")}
collars, surveys, assays, lith = (tables[n][1] for n in ("collars", "surveys", "assays", "lithology"))
col = {n: i for i, n in enumerate(tables["assays"][0])}
tags = {}


def tag(row, label):
    tags.setdefault(id(row), []).append(label)


candidates = sorted({r[0] for r in assays if r[0].startswith("DD") and len(of(assays, r[0])) >= 20})
(dup_id, dup_collar, no_assays, no_collar, overlap, inverted, beyond, gaps, no_survey,
 azi_flip, dip_flip, sentinels, text, twins, case, space_lith, space_collar) = rng.sample(candidates, 17)

c = of(collars, dup_id)[0]
new = [dup_id, f"{float(c[1]) + rng.uniform(180, 260):.1f}", f"{float(c[2]) - rng.uniform(120, 200):.1f}",
       f"{float(c[3]) + rng.uniform(-3, 3):.1f}", f"{float(c[4]) * rng.uniform(0.6, 0.8):.2f}", c[5]]
collars.insert(collars.index(c) + 1, new)
tag(c, "duplicate hole ID (original)")
tag(new, "duplicate hole ID (second collar, different place)")

c = of(collars, dup_collar)[0]
collars.insert(collars.index(c) + 1, list(c))
tag(c, "duplicated collar")
tag(collars[collars.index(c) + 1], "duplicated collar")

assays[:] = [r for r in assays if r[0] != no_assays]

collars.remove(of(collars, no_collar)[0])
for r in assays:
    if r[0] == no_collar:
        tag(r, "assays with no collar")

rows = of(assays, overlap)
for r in (rows[len(rows) // 3], rows[2 * len(rows) // 3]):
    r[1] = f"{float(r[1]) - rng.uniform(0.4, 0.9):.2f}"
    tag(r, "overlapping interval (FROM before previous TO)")

r = rng.choice(of(assays, inverted)[1:-1])
r[1], r[2] = r[2], r[1]
tag(r, "inverted interval (FROM > TO)")

rows = of(assays, beyond)
c = of(collars, beyond)[0]
c[4] = f"{float(rows[-3][1]) - 0.5:.2f}"
tag(c, "collar LENGTH shorter than assays")
for r in rows:
    if float(r[2]) > float(c[4]):
        tag(r, "interval beyond collar LENGTH")

rows = of(assays, gaps)
for r in (rows[len(rows) // 4], rows[3 * len(rows) // 4]):
    assays.remove(r)
    nxt = rows[rows.index(r) + 1]
    tag(nxt, f"gap before this row (missing {r[1]}-{r[2]})")

surveys[:] = [r for r in surveys if r[0] != no_survey]

r = of(surveys, azi_flip)[len(of(surveys, azi_flip)) // 2]
r[3] = f"{(float(r[3]) + 180) % 360:.2f}"
tag(r, "azimuth flipped by 180")

for r in of(surveys, dip_flip):
    r[2] = f"{-float(r[2]):.2f}"
    tag(r, "dip sign flipped")

rows = of(assays, sentinels)
for r, name, value in zip(rng.sample(rows, 5), ("ZN_PCT", "CU_PCT", "AG_GPT", "PB_PCT", "AU_GPT"),
                          ("-999", "-999", "-99", "-99", "-999")):
    r[col[name]] = value
    tag(r, f"{name} = {value}")

rows = of(assays, text)
r1, r2, r3 = rng.sample(rows, 3)
r1[col["CU_PCT"]] = "<0.01"
tag(r1, 'CU_PCT = "<0.01"')
r2[col["AU_GPT"]] = "<0.01"
tag(r2, 'AU_GPT = "<0.01"')
for name in ("ZN_PCT", "PB_PCT", "CU_PCT", "AG_GPT", "AU_GPT"):
    r3[col[name]] = "NS"
tag(r3, 'all grades = "NS"')

rows = of(assays, twins)
start = rng.randrange(len(rows) // 4, len(rows) - 3)
at = assays.index(rows[start + 2]) + 1
for r in rows[start:start + 3]:
    t = list(r)
    for name in ("ZN_PCT", "PB_PCT", "CU_PCT", "AG_GPT", "AU_GPT"):
        if t[col[name]]:
            t[col[name]] = jitter(t[col[name]], 0.08)
    assays.insert(at, t)
    at += 1
    tag(r, "twinned sample (original)")
    tag(t, "twinned sample (re-assay, same interval)")

rows = of(assays, case)
for r in rows[len(rows) // 2:len(rows) // 2 + 5]:
    r[0] = r[0].lower()
    tag(r, f"HOLE_ID lower case ({r[0]!r})")

for r in of(lith, space_lith)[1:3]:
    r[0] += " "
    tag(r, f"HOLE_ID trailing space ({r[0]!r})")

c = of(collars, space_collar)[0]
c[0] += " "
tag(c, f"HOLE_ID trailing space ({c[0]!r})")

print(f"no assays: {no_assays}; no collar: {no_collar}; no survey: {no_survey}")
for name, (header, rows) in tables.items():
    write(name + ".csv", header, rows)
    for line, r in enumerate(rows, start=2):
        for label in tags.get(id(r), []):
            print(f"{name}.csv line {line}: {r[0]!r} {label}")
