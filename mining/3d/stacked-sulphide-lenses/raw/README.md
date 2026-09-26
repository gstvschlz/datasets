# Stacked sulphide lenses, raw

The drill-hole tables of [Stacked sulphide lenses](../README.md) with typical data-entry errors planted, for practising
drill-hole validation. All 289 holes are kept; columns and conventions are those of the clean files.
`make_raw.py` rebuilds these files from the clean ones (fixed seed) and prints where each error landed.

Lines are file line numbers, the header being line 1. Every error is in a different `DD` hole.

| Error | Hole | File, lines |
|---|---|---|
| Duplicate hole ID: a second collar 290 m away, shorter | `DD0067` | `collars.csv` 69, 70 |
| Duplicated collar: same row entered twice | `DD0058` | `collars.csv` 59, 60 |
| Collar with no assays (mineralised in `lithology.csv`, assays dropped) | `DD0043` | `assays.csv` none |
| Assays, surveys and lithology with no collar | `DD0111` | `assays.csv` 5644–5770 |
| Overlapping intervals: `FROM` before the previous `TO` | `DD0200` | `assays.csv` 12274, 12297 |
| Inverted interval: `FROM` > `TO` | `DD0100` | `assays.csv` 4348 |
| Intervals beyond collar `LENGTH` (707.50 entered instead of 812.56; surveys and lithology go past it too) | `DD0055` | `collars.csv` 56; `assays.csv` 814–817 |
| Gaps: two missing samples, 475.73–477.75 and 532.43–534.42 | `DD0080` | `assays.csv` before 2387 and 2416 |
| Missing survey: no rows | `DD0151` | `surveys.csv` none |
| Azimuth flipped by 180° at one station (111.81 among ~292) | `DD0197` | `surveys.csv` 3215 |
| Dip sign flipped: whole hole entered negative | `DD0116` | `surveys.csv` 1918–1945 |
| Sentinels: `PB_PCT` −99, `CU_PCT` −999, `ZN_PCT` −999, `AG_GPT` −99, `AU_GPT` −999 | `DD0110` | `assays.csv` 5586, 5601, 5602, 5607, 5613 |
| Text in numeric columns: all grades `NS`; `CU_PCT` `<0.01`; `AU_GPT` `<0.01` | `DD0083` | `assays.csv` 2608, 2621, 2646 |
| Twinned samples: three intervals re-entered with grades within ±8% | `DD0162` | `assays.csv` 10483–10485 and 10486–10488 |
| `HOLE_ID` in lower case (`dd0062`) on five rows | `DD0062` | `assays.csv` 1181–1185 |
| `HOLE_ID` with a trailing space (`"DD0132 "`) | `DD0132` | `lithology.csv` 817, 818 |
| `HOLE_ID` with a trailing space (`"DD0104 "`), so no table matches it exactly | `DD0104` | `collars.csv` 107 |

Not errors, and also in the clean files: 111 holes, none with `MS`, `SMS` or `STR` logged, have no assays because
only mineralised zones are assayed; `RC0008`, `RC0014`, `RC0016` and `RC0031` have one unsampled gap each; `RC`
holes have no `AU_GPT` or `DENSITY`.
