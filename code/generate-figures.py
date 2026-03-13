"""
Generate Typst visual figures for A327094 optimal containers.
Colored grid cells: blue (filled), invisible (empty).
White grid lines separate cells within the polyomino.
Reads solver-results.json, outputs a327094-figures.typ.
Shows a(3)-a(9): matched prior authors' terms plus our proved a(9).
"""

import json
import os

CELL_MM = 7
FILL = "#4A90D9"


def status_badge(status_str):
    """Return (label, color) for status badge."""
    if "MATCHED" in status_str:
        return "MATCHED", "#6C757D"
    if "PROVED" in status_str:
        return "PROVED", "#27AE60"
    return "UPPER BOUND", "#E67E22"


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base, "..", "research", "solver-results.json")
    out_path = os.path.join(base, "..", "submission", "a327094-figures.typ")

    with open(json_path) as f:
        data = json.load(f)

    parts = []

    parts.append("""#set page(
  paper: "a4",
  margin: (top: 2cm, bottom: 2cm, left: 1.5cm, right: 1.5cm),
  header: context {
    if counter(page).get().first() > 1 [
      #align(center)[#text(size: 8pt, fill: luma(120))[A327094: Smallest Polyomino Containing All Free n-ominoes]]
    ]
  },
  footer: context {
    let current = counter(page).get().first()
    let total = counter(page).final().first()
    align(center)[#text(size: 8pt, fill: luma(120))[Page #current of #total]]
  },
)
#set text(font: "New Computer Modern", size: 9pt)
""")

    parts.append("""#align(center)[
  #text(size: 16pt, weight: "bold")[A327094: Smallest Polyomino Containing All Free n-ominoes]
  #v(0.3em)
  #text(size: 10pt)[Smallest connected polyomino that contains every free n-omino]
  #v(0.2em)
  #text(size: 10pt)[Proved Optimal: a(3) through a(9)]
  #v(0.2em)
  #text(size: 8pt, style: "italic")[Computed by Peter Exley, March 2026]
]
#v(0.5em)
#line(length: 100%, stroke: 0.5pt)
#v(0.3em)
""")

    for n in range(3, 10):
        key = str(n)
        if key not in data:
            continue
        rec = data[key]
        cells = [(c[0], c[1]) for c in rec["cells"]]
        size = rec["size"]
        rows, cols = rec["grid_size"]
        status = rec.get("status", "PROVED")
        num_polys = rec.get("num_free_polyominoes", "?")

        min_r = min(r for r, c in cells)
        min_c = min(c for r, c in cells)
        filled = set((r - min_r, c - min_c) for r, c in cells)

        badge_label, badge_color = status_badge(status)

        cell_lines = []
        for r in range(rows):
            for c in range(cols):
                if (r, c) in filled:
                    cell_lines.append(
                        f'      table.cell(fill: rgb("{FILL}"))[]'
                    )
                else:
                    cell_lines.append(
                        '      table.cell(fill: white)[]'
                    )
        cells_str = ",\n".join(cell_lines)

        parts.append(f"""#block(breakable: false, width: 100%)[
  #align(center)[
    #text(size: 11pt, weight: "bold")[a({n}) = {size}]
    #h(0.5em)
    #text(size: 8pt, weight: "bold", fill: rgb("{badge_color}"))[\\[{badge_label}\\]]
  ]
  #align(center)[
    #text(size: 8pt)[{rows} X {cols} bounding box, contains all {num_polys} free {n}-ominoes]
  ]
  #v(0.3em)
  #align(center)[
    #table(
      columns: ({CELL_MM}mm,) * {cols},
      rows: ({CELL_MM}mm,) * {rows},
      inset: 0pt,
      stroke: 0.5pt + white,
{cells_str},
    )
  ]
  #v(0.5em)
]
""")

    parts.append("""#v(0.5em)
#line(length: 100%, stroke: 0.5pt)
""")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))

    print(f"Generated: {out_path}")
    print(f"Compile with: typst compile {out_path}")


if __name__ == "__main__":
    main()
