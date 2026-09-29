"""Cut seismic.sgy from the F3 dip-steered median subvolume (IL 230-430, XL 475-675, 1600-1800 ms).

    python crop.py F3_Dip_steered_median_subvolume_IL230-430_XL475-675_T1600-1800.sgy

Copies the textual and binary headers and every trace with IL 320-364 and XL 580-624
byte for byte: all samples and the original trace headers are kept.
"""

import struct
import sys
from pathlib import Path

INLINES = range(320, 365)
CROSSLINES = range(580, 625)

src = Path(sys.argv[1]).read_bytes()
ns = struct.unpack(">H", src[3220:3222])[0]
size = 240 + 4 * ns
out = bytearray(src[:3600])
for start in range(3600, len(src), size):
    il, xl = struct.unpack(">ii", src[start + 188 : start + 196])
    if il in INLINES and xl in CROSSLINES:
        out += src[start : start + size]
assert len(out) == 3600 + len(INLINES) * len(CROSSLINES) * size
Path(__file__).with_name("seismic.sgy").write_bytes(out)
