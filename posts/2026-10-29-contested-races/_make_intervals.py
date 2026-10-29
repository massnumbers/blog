"""Derive 75% predictive intervals for every 2026 target race.

The election-modeling snapshot publishes only 90% bounds (the 5th and 95th
percentiles of each race's posterior predictive draws). This script reads the
per-race draws from the 14d-r2 interactive bundle, checks that it reproduces
the published 90% bounds, and writes the 12.5th and 87.5th percentiles to
forecast_14d_r2_intervals.csv. Quantiles use linear interpolation, matching
numpy.quantile's default as used by the model. Run from the repository root:

    python3 posts/2026-10-29-contested-races/_make_intervals.py
"""

import csv
import glob
import json
from pathlib import Path

POST_DIR = Path("posts/2026-10-29-contested-races")
BUNDLE = Path("../../bwbensonjr/election-modeling/data/forecast/2026/interactive/14d-r2")


def quantile(values, p):
    xs = sorted(values)
    pos = p * (len(xs) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


races = {r["target_id"]: r for r in csv.DictReader(open(POST_DIR / "forecast_14d_r2_races.csv"))}

rows = []
for path in sorted(glob.glob(str(BUNDLE / "races" / "*.json"))):
    race = json.load(open(path))
    target_id = race["target_id"]
    if target_id not in races:
        continue
    draws = race["draws"]
    for p, col in [(0.05, "lower_90"), (0.95, "upper_90")]:
        published = float(races[target_id][col])
        assert abs(quantile(draws, p) - published) < 1e-6, (target_id, col)
    rows.append({
        "target_id": target_id,
        "lower_75": quantile(draws, 0.125),
        "upper_75": quantile(draws, 0.875),
    })

assert len(rows) == len(races), (len(rows), len(races))

with open(POST_DIR / "forecast_14d_r2_intervals.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["target_id", "lower_75", "upper_75"])
    writer.writeheader()
    writer.writerows(sorted(rows, key=lambda r: r["target_id"]))

print(f"wrote {len(rows)} races")
