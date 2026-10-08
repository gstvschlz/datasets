"""Build the f3-survey files from dGB's F3_Demo_2023.zip (TerraNubis, CC BY-SA 3.0).

    python make.py F3_Demo_2023.zip

Writes into this folder: seismic.sgy (byte-for-byte copy of Rawdata/Seismic_data.sgy),
horizons.csv, faults.csv, wells.csv, logs.csv, tops.csv, checkshots.csv.
Wells are vertical: Z = KB - MD.
"""

import io
import shutil
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = "F3_Demo_2023/Rawdata/"
WELLS = "All_wells_RawData/"
NULL = "-999.2500"
CURVES = ["RHOB", "DT", "GR", "AI", "AI_REL", "PHIE"]  # LAS order after DEPTH

project = zipfile.ZipFile(sys.argv[1])
wells = zipfile.ZipFile(io.BytesIO(project.read(RAW + "Well_data/All_wells_RawData.zip")))


def lines(archive, name):
    return [line.split() for line in archive.read(name).decode("latin1").splitlines() if line.strip()]


def write(name, header, rows):
    with open(HERE / name, "w", newline="\n") as f:
        f.write(",".join(header) + "\n")
        for row in rows:
            f.write(",".join(str(v) for v in row) + "\n")


with project.open(RAW + "Seismic_data.sgy") as src, open(HERE / "seismic.sgy", "wb") as dst:
    shutil.copyfileobj(src, dst, 1 << 24)


def horizons():
    for name in sorted(project.namelist()):
        if name.startswith(RAW + "Surface_data/") and name.endswith(".txt"):
            horizon = name.rsplit("/", 1)[1].removeprefix("F3-Horizon-").removesuffix(".txt")
            for x, y, t in lines(project, name):
                yield horizon, x, y, t


write("horizons.csv", ["HORIZON", "X", "Y", "TWT_MS"], horizons())
write("faults.csv", ["FAULT", "STICK", "NODE", "X", "Y", "TWT_MS"],
      (("FaultA", stick, node, x, y, t)
       for x, y, t, stick, node in lines(project, RAW + "Faults/FaultA.txt")))

names = sorted(n.rsplit("/", 1)[1].removesuffix(".track")
               for n in wells.namelist() if n.endswith(".track"))
kb, head = {}, {}
for well in names:
    top = lines(wells, f"{WELLS}Track/{well}.track")[0]  # X Y TVDSS MD
    kb[well] = round(float(top[3]) - float(top[2]), 2)  # MD - TVDSS at the top
    head[well] = (top[0], top[1], f"{kb[well]:g}")


def z(well, md):
    return f"{round(kb[well] - float(md), 2):g}"


def number(text):
    """The value as published, without trailing zeros."""
    return text.rstrip("0").rstrip(".") if "." in text else text


def logs():
    for well in names:
        text = wells.read(f"{WELLS}Lasfiles/{well}_logs.las").decode("latin1")
        for line in text[text.index("~A"):].splitlines()[1:]:
            values = line.split()
            if len(values) == 7 and any(v != NULL for v in values[1:]):
                md = values[0]
                yield [well, number(md), z(well, md)] + ["" if v == NULL else number(v) for v in values[1:]]


write("logs.csv", ["WELL", "MD", "Z", *CURVES], logs())


def tops():
    for well in names:
        for row in lines(wells, f"{WELLS}Tops/{well}_markers.txt"):
            if len(row) > 1:
                yield well, " ".join(row[1:]), row[0], z(well, row[0])


def checkshots():
    for well in names:
        for md, twt in lines(wells, f"{WELLS}Checkshot/{well}_TD.txt"):
            yield well, md, z(well, md), f"{float(twt) * 1000:g}"


write("tops.csv", ["WELL", "SURFACE", "MD", "Z"], tops())
write("checkshots.csv", ["WELL", "MD", "Z", "TWT_MS"], checkshots())


# The tracks stop short of the deepest tops and checkshots: TD is the deepest MD in any file.
td = {}
for name in ("logs.csv", "tops.csv", "checkshots.csv"):
    with open(HERE / name) as f:
        for row in list(f)[1:]:
            cells = row.split(",")
            md = float(cells[2] if name == "tops.csv" else cells[1])
            td[cells[0]] = max(td.get(cells[0], 0), md)
write("wells.csv", ["WELL", "X", "Y", "KB", "TD_MD"],
      ((well, *head[well], f"{td[well]:g}") for well in names))
