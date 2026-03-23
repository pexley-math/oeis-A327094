#!/usr/bin/env python3
"""Generate publication and understanding figures for A327094.

Reads solver-results.json and produces:
  1. submission/a327094-figures.typ -- publication PDF (our new terms only: a(9), a(10))
  2. research/a327094-understanding.typ -- personal understanding diagram
"""

import json
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_SCRIPT_DIR)
_PAPER_DIR = os.path.dirname(_PROJECT_DIR)
if _PAPER_DIR not in sys.path:
    sys.path.insert(0, _PAPER_DIR)

from figure_gen_utils.document_builder import DocumentBuilder


def load_results():
    path = os.path.join(_PROJECT_DIR, "research", "solver-results.json")
    with open(path) as f:
        return json.load(f)


def make_cell_set(result):
    """Convert result cells to set of (r,c) tuples."""
    return set(tuple(c) for c in result["cells"])


def publication_figures(results):
    """Generate publication PDF showing only OUR new terms (a(9), a(10))."""
    doc = DocumentBuilder(
        title="A327094: Smallest Polyomino Containing All Free $n$-ominoes",
        description="$a(n)$ = minimum cells in a polyomino containing "
                    "all free $n$-ominoes as subshapes",
        sequence_line="$a(9) = 26$, $a(10) = 31$",
    )

    # Only show our new contributions: a(9) and a(10)
    for n_str in ["9", "10"]:
        r = results[n_str]
        cells = make_cell_set(r)
        gh, gw = r["grid_size"]
        n = r["n"]
        k = r["size"]
        pieces = r["num_free_polyominoes"]

        doc.add_binary_figure(
            cells, bbox_rows=gh, bbox_cols=gw, n=n, k=k,
            status="PROVED", mode="container",
            detail_text=(f"{gh} \\u{{00D7}} {gw} bounding box, "
                         f"{k} cells, contains all {pieces} free "
                         f"{n}-ominoes"),
        )

    out = os.path.join(_PROJECT_DIR, "submission", "a327094-figures.typ")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    doc.generate(out)
    print(f"Publication figures: {out}")
    return out


def understanding_figure(results):
    """Generate personal understanding diagram for a(5) and a(10)."""
    doc = DocumentBuilder(
        title="A327094: Understanding Diagram",
        description="What does a container polyomino look like?",
        sequence_line="Selected terms: $a(5) = 9$, $a(10) = 31$",
    )

    # a(5) = 9: small enough to visualise piece containment
    r5 = results["5"]
    cells5 = make_cell_set(r5)
    doc.add_binary_figure(
        cells5, bbox_rows=r5["grid_size"][0], bbox_cols=r5["grid_size"][1],
        n=5, k=9, status="PROVED", mode="container",
        detail_text="9 cells on 3x5 grid. Contains all 12 free pentominoes.",
    )

    # a(10) = 31: the frontier term with staircase structure
    r10 = results["10"]
    cells10 = make_cell_set(r10)
    doc.add_binary_figure(
        cells10, bbox_rows=r10["grid_size"][0], bbox_cols=r10["grid_size"][1],
        n=10, k=31, status="PROVED", mode="container",
        detail_text=("31 cells on 5x10 grid. Contains all 4655 free "
                     "10-ominoes. Staircase pattern: rows 10, 8, 6, 4, 3."),
    )

    out = os.path.join(_PROJECT_DIR, "research", "a327094-understanding.typ")
    doc.generate(out)
    print(f"Understanding figure: {out}")
    return out


def main():
    results = load_results()

    pub_path = publication_figures(results)
    und_path = understanding_figure(results)

    # Compile if typst is available
    from figure_gen_utils.typst_page import compile_typst
    for path in [pub_path, und_path]:
        try:
            compile_typst(path)
            print(f"  Compiled: {path.replace('.typ', '.pdf')}")
        except Exception as e:
            print(f"  Typst compile failed for {path}: {e}")


if __name__ == "__main__":
    main()
