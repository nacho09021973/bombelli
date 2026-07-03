#!/usr/bin/env python3
"""Render the Bombelli-defaults-vs-tuned schedule comparison as a static SVG.

Reads data/schedule_comparison.csv (produced by ``python experiments.py
schedule``) and writes a two-panel bar chart: mean final energy and
zero-energy runs, for the default and tuned annealing schedules on the
12-element benchmark (see README "Finding I").
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import NamedTuple

SERIES_COLORS = {
    "bombelli_defaults": "#2a78d6",
    "tuned": "#1baf7a",
}
SERIES_LABELS = {
    "bombelli_defaults": "Bombelli defaults",
    "tuned": "Tuned schedule",
}


class ScheduleRow(NamedTuple):
    label: str
    initial_temp: float
    cooling_factor: float
    mean_final_energy: float
    zero_energy_runs: int
    n_seeds: int


def read_rows(csv_path: Path) -> list[ScheduleRow]:
    rows: list[ScheduleRow] = []
    with csv_path.open(newline="", encoding="utf-8") as fh:
        for record in csv.DictReader(fh):
            numerator, _, denominator = record["zero_energy_runs"].partition("/")
            rows.append(
                ScheduleRow(
                    label=record["schedule_label"],
                    initial_temp=float(record["initial_temp"]),
                    cooling_factor=float(record["cooling_factor"]),
                    mean_final_energy=float(record["mean_final_energy"]),
                    zero_energy_runs=int(numerator),
                    n_seeds=int(denominator),
                )
            )
    return rows


def _bar_path(x: float, width: float, base_y: float, top_y: float, radius: float) -> str:
    height = base_y - top_y
    r = min(radius, height, width / 2) if height > 0 else 0.0
    return (
        f"M {x} {base_y} "
        f"L {x} {top_y + r} "
        f"Q {x} {top_y} {x + r} {top_y} "
        f"L {x + width - r} {top_y} "
        f"Q {x + width} {top_y} {x + width} {top_y + r} "
        f"L {x + width} {base_y} Z"
    )


def _panel_svg(
    *,
    x0: float,
    panel_width: float,
    panel_height: float,
    title: str,
    note: str,
    rows: list[ScheduleRow],
    values: list[float],
    value_format: str,
    axis_max: float,
    tick_count: int = 4,
) -> str:
    margin_top = 44.0
    margin_bottom = 40.0
    margin_left = 34.0
    margin_right = 16.0
    plot_w = panel_width - margin_left - margin_right
    plot_h = panel_height - margin_top - margin_bottom
    base_y = margin_top + plot_h

    parts = [
        f'<text x="{x0 + panel_width / 2:.1f}" y="18" text-anchor="middle" '
        f'font-family="Georgia, serif" font-size="15" fill="#222">{title}</text>',
        f'<text x="{x0 + panel_width / 2:.1f}" y="34" text-anchor="middle" '
        f'font-family="monospace" font-size="10.5" fill="#5a534b">{note}</text>',
    ]

    for i in range(tick_count + 1):
        v = axis_max / tick_count * i
        y = base_y - (v / axis_max) * plot_h
        parts.append(
            f'<line x1="{x0 + margin_left:.1f}" x2="{x0 + panel_width - margin_right:.1f}" '
            f'y1="{y:.1f}" y2="{y:.1f}" stroke="#d8d1c6" stroke-width="1" />'
        )
        parts.append(
            f'<text x="{x0 + margin_left - 6:.1f}" y="{y + 3:.1f}" text-anchor="end" '
            f'font-family="monospace" font-size="9" fill="#898781">{v:.0f}</text>'
        )

    parts.append(
        f'<line x1="{x0 + margin_left:.1f}" x2="{x0 + panel_width - margin_right:.1f}" '
        f'y1="{base_y:.1f}" y2="{base_y:.1f}" stroke="#c3c2b7" stroke-width="1" />'
    )

    slot = plot_w / len(rows)
    bar_width = min(56.0, slot * 0.5)
    for i, (row, value) in enumerate(zip(rows, values)):
        slot_x = x0 + margin_left + i * slot
        bar_x = slot_x + (slot - bar_width) / 2
        bar_h = (value / axis_max) * plot_h if axis_max else 0.0
        top_y = base_y - bar_h
        color = SERIES_COLORS[row.label]
        parts.append(
            f'<path d="{_bar_path(bar_x, bar_width, base_y, top_y, 4.0)}" fill="{color}" />'
        )
        parts.append(
            f'<text x="{bar_x + bar_width / 2:.1f}" y="{top_y - 8:.1f}" text-anchor="middle" '
            f'font-family="monospace" font-size="12" font-weight="bold" fill="#171512">'
            f"{value_format.format(value)}</text>"
        )
        parts.append(
            f'<text x="{bar_x + bar_width / 2:.1f}" y="{base_y + 15:.1f}" text-anchor="middle" '
            f'font-family="monospace" font-size="9.5" fill="#5a534b">'
            f"T&#8320;={row.initial_temp:g}, &#945;={row.cooling_factor:g}</text>"
        )

    return "\n".join(parts)


def write_schedule_chart(rows: list[ScheduleRow], path: Path) -> None:
    width, height = 760, 320
    panel_width = width / 2
    legend_swatches = "".join(
        f'<rect x="{28 + i * 190}" y="{height - 20}" width="10" height="10" rx="3" '
        f'fill="{SERIES_COLORS[row.label]}" />'
        f'<text x="{44 + i * 190}" y="{height - 11}" font-family="monospace" '
        f'font-size="10.5" fill="#5a534b">{SERIES_LABELS[row.label]}</text>'
        for i, row in enumerate(rows)
    )

    energy_panel = _panel_svg(
        x0=0,
        panel_width=panel_width,
        panel_height=height - 40,
        title="Mean final energy",
        note="100 seeds, 12-element benchmark - lower is better",
        rows=rows,
        values=[row.mean_final_energy for row in rows],
        value_format="{:.3f}",
        axis_max=25.0,
    )
    zero_panel = _panel_svg(
        x0=panel_width,
        panel_width=panel_width,
        panel_height=height - 40,
        title="Zero-energy runs",
        note="out of 100 seeds - higher is better",
        rows=rows,
        values=[float(row.zero_energy_runs) for row in rows],
        value_format="{:.0f}/100",
        axis_max=100.0,
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#fbfaf7" />
  {energy_panel}
  {zero_panel}
  <line x1="{panel_width}" x2="{panel_width}" y1="10" y2="{height - 34}" stroke="#e1e0d9" stroke-width="1" />
  {legend_swatches}
</svg>
"""
    path.write_text(svg, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv", type=Path, default=Path("data/schedule_comparison.csv"),
        help="input CSV (default: data/schedule_comparison.csv)",
    )
    parser.add_argument(
        "--output", type=Path, default=Path("schedule_comparison.svg"),
        help="output SVG path (default: schedule_comparison.svg)",
    )
    args = parser.parse_args()

    rows = read_rows(args.csv)
    write_schedule_chart(rows, args.output)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
