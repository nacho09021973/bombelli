#!/usr/bin/env python3
"""Draw small causal sets as 1980s-style SVG diagrams.

The goal is not to make a technical plotting package. This script is a
small divulgative companion for the examples in ``inputs/``: it places
events by causal level, draws only the covering relations, and uses a
dark CRT-like palette so the structure is easy to inspect at a glance.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import causet_invariants
import cones


Point = Tuple[float, float]


def _layout_by_levels(z: Sequence[Sequence[bool]]) -> List[Point]:
    """Place each element by longest-chain level and within-level order."""

    profile = causet_invariants.antichain_profile(z)
    level_of: List[int] = []
    for lv, count in enumerate(profile):
        level_of.extend([lv] * count)

    # Recompute robustly by element index. The profile alone gives counts,
    # not membership, and the labels are topological but not level-grouped.
    levels: Dict[int, List[int]] = {}
    element_level = [0] * len(z)
    for j in range(len(z)):
        best = -1
        for i in range(j):
            if z[i][j] and element_level[i] > best:
                best = element_level[i]
        element_level[j] = best + 1
        levels.setdefault(element_level[j], []).append(j)

    max_level = max(levels) if levels else 0
    coords: List[Point] = [(0.0, 0.0)] * len(z)
    for level, indices in levels.items():
        y = 0.5 if max_level == 0 else level / max_level
        count = len(indices)
        for pos, idx in enumerate(indices):
            x = 0.5 if count == 1 else (pos + 1) / (count + 1)
            coords[idx] = (x, y)
    return coords


def _svg_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def write_retro_svg(
    z: Sequence[Sequence[bool]],
    output: Path,
    *,
    title: str,
    show_labels: bool = True,
) -> None:
    width = 1000
    height = 680
    margin_x = 120
    margin_y = 110
    coords = _layout_by_levels(z)
    links = cones.transitive_reduction(z)
    profile = causet_invariants.antichain_profile(z)
    mm_dim = causet_invariants.myrheim_meyer_dimension(z)

    def sx(x: float) -> float:
        return margin_x + x * (width - 2 * margin_x)

    def sy(y: float) -> float:
        return height - margin_y - y * (height - 2 * margin_y)

    grid_lines = []
    for x in range(80, width, 80):
        grid_lines.append(
            f"<line x1='{x}' y1='0' x2='{x}' y2='{height}' class='grid' />"
        )
    for y in range(80, height, 80):
        grid_lines.append(
            f"<line x1='0' y1='{y}' x2='{width}' y2='{y}' class='grid' />"
        )

    edge_lines = []
    for i, j in links:
        x1, y1 = coords[i]
        x2, y2 = coords[j]
        edge_lines.append(
            f"<line x1='{sx(x1):.2f}' y1='{sy(y1):.2f}' "
            f"x2='{sx(x2):.2f}' y2='{sy(y2):.2f}' class='edge' />"
        )

    nodes = []
    for idx, (x, y) in enumerate(coords):
        px = sx(x)
        py = sy(y)
        hue = 185 + (idx * 23) % 95
        nodes.append(
            f"<circle cx='{px:.2f}' cy='{py:.2f}' r='18' "
            f"fill='hsl({hue}, 95%, 58%)' class='node' />"
        )
        nodes.append(
            f"<circle cx='{px:.2f}' cy='{py:.2f}' r='5' fill='#fff8b8' opacity='0.95' />"
        )
        if show_labels:
            nodes.append(
                f"<text x='{px:.2f}' y='{py + 42:.2f}' class='label'>{idx + 1}</text>"
            )

    level_labels = []
    for level in range(len(profile)):
        y = sy(0.5 if len(profile) == 1 else level / (len(profile) - 1))
        level_labels.append(
            f"<text x='36' y='{y + 5:.2f}' class='level'>L{level}</text>"
        )

    safe_title = _svg_escape(title)
    safe_profile = _svg_escape(str(profile))
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>
  <defs>
    <filter id='glow'>
      <feGaussianBlur stdDeviation='3.4' result='blur'/>
      <feMerge>
        <feMergeNode in='blur'/>
        <feMergeNode in='SourceGraphic'/>
      </feMerge>
    </filter>
    <linearGradient id='screen' x1='0' y1='0' x2='0' y2='1'>
      <stop offset='0%' stop-color='#18002e'/>
      <stop offset='55%' stop-color='#061733'/>
      <stop offset='100%' stop-color='#05070f'/>
    </linearGradient>
    <style>
      .grid {{ stroke: #36f7ff; stroke-width: 1; opacity: 0.10; }}
      .edge {{ stroke: #ff4fd8; stroke-width: 3.2; opacity: 0.78; filter: url(#glow); }}
      .node {{ stroke: #fff8b8; stroke-width: 2.2; filter: url(#glow); }}
      .title {{ fill: #fff8b8; font: 700 30px 'Courier New', monospace; letter-spacing: 0; }}
      .subtitle {{ fill: #67f7ff; font: 16px 'Courier New', monospace; letter-spacing: 0; }}
      .label {{ fill: #fff8b8; font: 700 15px 'Courier New', monospace; text-anchor: middle; }}
      .level {{ fill: #67f7ff; font: 700 14px 'Courier New', monospace; opacity: 0.85; }}
      .caption {{ fill: #d5d8ff; font: 14px 'Courier New', monospace; }}
    </style>
  </defs>
  <rect width='100%' height='100%' fill='url(#screen)' />
  <rect x='18' y='18' width='{width - 36}' height='{height - 36}' rx='18' fill='none' stroke='#67f7ff' stroke-width='2' opacity='0.75' />
  {"".join(grid_lines)}
  <text x='48' y='58' class='title'>{safe_title}</text>
  <text x='50' y='84' class='subtitle'>causal set / transitive reduction / retro view</text>
  {"".join(level_labels)}
  {"".join(edge_lines)}
  {"".join(nodes)}
  <text x='50' y='{height - 48}' class='caption'>n={len(z)} · links={len(links)} · height={causet_invariants.height(z)} · MM dimension ≈ {mm_dim:.2f} · levels={safe_profile}</text>
</svg>
"""
    output.write_text(svg, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create an 1980s-style SVG visualization of a small causal set."
    )
    parser.add_argument("input_file", type=Path, help="Pascal-style incidence input file")
    parser.add_argument(
        "--output",
        type=Path,
        help="SVG output path; default: input filename with .retro.svg",
    )
    parser.add_argument("--title", help="title shown in the SVG")
    parser.add_argument("--no-labels", action="store_true", help="hide event numbers")
    args = parser.parse_args()

    z = cones.parse_cones_input(args.input_file)
    output = args.output or args.input_file.with_suffix(".retro.svg")
    title = args.title or args.input_file.stem.replace("_", " ")
    write_retro_svg(z, output, title=title, show_labels=not args.no_labels)
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
