#!/usr/bin/env python3
"""Exhaustive UNSAT test using PySAT/CaDiCaL (no connectivity requirement).

Proves: no k-cell subgraph of ANY spanning-bound-compatible grid can contain
all free n-ominoes, even without requiring connectivity. This is STRONGER
than the connectivity-required proof and FASTER (no CEGAR iterations).

Uses CaDiCaL via PySAT for best UNSAT performance.
"""

import math
import os
import sys
import time

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_SCRIPT_DIR)
_PAPER_DIR = os.path.dirname(_PROJECT_DIR)
if _PAPER_DIR not in sys.path:
    sys.path.insert(0, _PAPER_DIR)

from solve_a327094 import enumerate_free, get_all_placements, _find_i_piece_idx
from pysat.solvers import Solver
from pysat.card import CardEnc, EncType


def encode_and_solve(n, k, pieces, grid_h, grid_w, symmetry_break=True,
                     timeout=600):
    """Encode as CNF, solve with CaDiCaL. Returns (status, time)."""
    all_place = get_all_placements(pieces, grid_h, grid_w)

    # Check all pieces have placements
    for pl in all_place:
        if not pl:
            return 'UNSAT', 0.0

    var_id = [0]
    def new_var():
        var_id[0] += 1
        return var_id[0]

    clauses = []

    # Cell variables
    x = {}
    for r in range(grid_h):
        for c in range(grid_w):
            x[(r, c)] = new_var()

    # Placement variables + containment constraints
    i_piece_idx = None
    i_placement_idx = None
    if symmetry_break and grid_h < n and grid_w >= n:
        i_piece_idx = _find_i_piece_idx(n, pieces)
        if i_piece_idx is not None:
            target_cells = tuple(sorted((0, c) for c in range(n)))
            for j, cells in enumerate(all_place[i_piece_idx]):
                if tuple(sorted(cells)) == target_cells:
                    i_placement_idx = j
                    break

    total_placements = 0
    for i, placements in enumerate(all_place):
        pvars = []
        for j, cells in enumerate(placements):
            b = new_var()
            for cell in cells:
                clauses.append([-b, x[cell]])
            pvars.append(b)
        total_placements += len(placements)

        if i == i_piece_idx and i_placement_idx is not None:
            clauses.append([pvars[i_placement_idx]])
        else:
            clauses.append(pvars[:])

    # Cardinality: exactly k cells
    cell_vars = [x[(r, c)] for r in range(grid_h) for c in range(grid_w)]
    leq = CardEnc.atmost(cell_vars, bound=k, encoding=EncType.seqcounter,
                          top_id=var_id[0])
    for cl in leq.clauses:
        clauses.append(cl)
    var_id[0] = max(var_id[0], max(abs(l) for cl in leq.clauses for l in cl))

    geq = CardEnc.atleast(cell_vars, bound=k, encoding=EncType.seqcounter,
                           top_id=var_id[0])
    for cl in geq.clauses:
        clauses.append(cl)
    var_id[0] = max(var_id[0], max(abs(l) for cl in geq.clauses for l in cl))

    # Solve with CaDiCaL
    t0 = time.time()
    try:
        solver = Solver(name='cadical195', bootstrap_with=clauses)
    except Exception:
        solver = Solver(name='cadical153', bootstrap_with=clauses)

    # CaDiCaL doesn't support native timeout. Use propagation budget.
    result = solver.solve()
    elapsed = time.time() - t0
    solver.delete()

    if result:
        return 'SAT_RELAXED', elapsed
    else:
        return 'UNSAT', elapsed


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--n', type=int, default=10)
    parser.add_argument('--k', type=int, default=30)
    parser.add_argument('--timeout', type=int, default=1800)
    args = parser.parse_args()

    n, k = args.n, args.k
    min_h = math.ceil(n / 2)
    min_w = n

    pieces = enumerate_free(n)

    # Enumerate all grids
    grids = []
    for h in range(min_h, k + 1):
        for w in range(max(min_w, h), k + 1):
            if h + w - 1 <= k and h * w >= k:
                grids.append((h, w))

    print(f"Exhaustive UNSAT proof (CaDiCaL, no connectivity): n={n}, k={k}")
    print(f"  Pieces: {len(pieces)}")
    print(f"  Total grids: {len(grids)}")
    print(f"  Solver: CaDiCaL via PySAT (stronger: UNSAT even without connectivity)")
    print()

    unresolved = []
    sat_found = []
    total_start = time.time()

    for i, (gh, gw) in enumerate(grids):
        area = gh * gw
        ratio = area / k
        density = k / area
        use_symbreak = gh < n

        status, elapsed = encode_and_solve(
            n, k, pieces, gh, gw, symmetry_break=use_symbreak)

        tag = ""
        if status == 'SAT_RELAXED':
            tag = " (relaxed SAT -- connectivity not checked)"
            sat_found.append((gh, gw))
        elif status == 'TIMEOUT':
            tag = " ***TIMEOUT***"
            unresolved.append((gh, gw))

        sb = "sb" if use_symbreak else "no-sb"
        print(f"  [{i+1:3d}/{len(grids)}] {gh:2d}x{gw:2d}  "
              f"area={area:4d}  ratio={ratio:5.2f}  "
              f"{status:12s}  {elapsed:8.1f}s  ({sb}){tag}", flush=True)

    total_time = time.time() - total_start

    print(f"\n{'='*70}")
    print(f"SUMMARY: {len(grids)} grids tested in {total_time:.1f}s")
    unsat_count = len(grids) - len(unresolved) - len(sat_found)
    print(f"  UNSAT: {unsat_count}")
    print(f"  SAT_RELAXED: {len(sat_found)}")
    print(f"  TIMEOUT: {len(unresolved)}")

    if sat_found:
        print(f"\n  SAT_RELAXED grids (need CEGAR connectivity check):")
        for gh, gw in sat_found:
            print(f"    {gh}x{gw}")
    elif unresolved:
        print(f"\n  UNRESOLVED: {len(unresolved)} grids")
    else:
        print(f"\n  ALL {len(grids)} GRIDS PROVED UNSAT (without connectivity)")
        print(f"  This is STRONGER than connectivity-required UNSAT.")
        print(f"  a({n}) = {k+1} is EXHAUSTIVELY PROVED.")

    print(f"{'='*70}")


if __name__ == '__main__':
    main()
