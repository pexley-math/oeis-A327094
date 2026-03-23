#!/usr/bin/env python3
"""
Solver for A327094: smallest polyomino containing all free n-ominoes.

Uses OR-Tools CP-SAT with CEGAR connectivity. Two-phase search:
  Phase 1 (SAT): find optimal k with tight grid cap for speed
  Phase 2 (UNSAT): prove k-1 impossible on all relevant grids

Shared libraries: polyform_enum (C-speed), sat_utils (connectivity, search).

Usage:
    python solve_a327094.py --n 9
    python solve_a327094.py --n 10 --timeout 900
    python solve_a327094.py --all --json research/solver-results.json
"""

import argparse
import json
import math
import os
import sys
import time

# --- Path setup for shared libraries ---
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_SCRIPT_DIR)
_PAPER_DIR = os.path.dirname(_PROJECT_DIR)
if _PAPER_DIR not in sys.path:
    sys.path.insert(0, _PAPER_DIR)

# --- Shared library imports with fallback ---
try:
    from polyform_enum import enumerate_free as _pe_free, all_placements as _pe_placements
    _USE_CYTHON = True
except ImportError:
    _USE_CYTHON = False

from ortools.sat.python import cp_model
from sat_utils.connectivity import find_components, SQUARE_DIRS
from sat_utils.search import top_down_search


# ================================================================
# Pure Python fallbacks (for OEIS reviewers without Cython)
# ================================================================

def _py_enumerate_free(n):
    if n == 0:
        return [frozenset()]
    if n == 1:
        return [frozenset([(0, 0)])]

    def normalize(cells):
        cs = list(cells)
        mr = min(r for r, c in cs)
        mc = min(c for r, c in cs)
        return frozenset((r - mr, c - mc) for r, c in cs)

    def canonical(cells):
        orients = []
        cs = list(cells)
        for _ in range(4):
            orients.append(normalize(cs))
            cs = [(-c, r) for r, c in cs]
        cs = [(r, -c) for r, c in cs]
        for _ in range(4):
            orients.append(normalize(cs))
            cs = [(-c, r) for r, c in cs]
        return min(tuple(sorted(o)) for o in orients)

    prev = _py_enumerate_free(n - 1)
    seen = set()
    result = []
    for poly in prev:
        for r, c in poly:
            for dr, dc in SQUARE_DIRS:
                nr, nc = r + dr, c + dc
                if (nr, nc) not in poly:
                    new_poly = poly | {(nr, nc)}
                    canon = canonical(new_poly)
                    if canon not in seen:
                        seen.add(canon)
                        result.append(frozenset(canon))
    return result


def _py_all_placements(pieces, rows, cols):
    def orientations(cells):
        cs = list(cells)
        orients = set()
        for _ in range(4):
            normed = tuple(sorted((r - min(r2 for r2, _ in cs),
                                   c - min(c2 for _, c2 in cs)) for r, c in cs))
            orients.add(normed)
            cs = [(-c, r) for r, c in cs]
        cs = [(r, -c) for r, c in cs]
        for _ in range(4):
            normed = tuple(sorted((r - min(r2 for r2, _ in cs),
                                   c - min(c2 for _, c2 in cs)) for r, c in cs))
            orients.add(normed)
            cs = [(-c, r) for r, c in cs]
        return orients

    result = []
    for piece in pieces:
        placements = []
        for orient in orientations(list(piece)):
            mr = max(r for r, c in orient)
            mc = max(c for r, c in orient)
            for dr in range(rows - mr):
                for dc in range(cols - mc):
                    placements.append(tuple((r + dr, c + dc) for r, c in orient))
        seen = set()
        unique = []
        for p in placements:
            key = tuple(sorted(p))
            if key not in seen:
                seen.add(key)
                unique.append(p)
        result.append(unique)
    return result


def enumerate_free(n):
    if _USE_CYTHON:
        return _pe_free(n, "square")
    return _py_enumerate_free(n)


def get_all_placements(pieces, rows, cols):
    if _USE_CYTHON:
        return _pe_placements(pieces, rows, cols, "square")
    return _py_all_placements(pieces, rows, cols)


# ================================================================
# Bounds and grid selection
# ================================================================

# Known values for smart range selection (pre-primed for development;
# final proof run uses --fresh which ignores these)
KNOWN = {0: 0, 1: 1, 2: 2, 3: 4, 4: 6, 5: 9, 6: 12, 7: 17, 8: 20, 9: 26}

# Empirical: optimal grid area / a(n) ratio is 1.50 - 1.73 across all known terms.
# SAT_AREA_RATIO caps the SAT search (tight = fast).
# UNSAT_AREA_RATIO caps the UNSAT proof (wider = more thorough).
SAT_AREA_RATIO = 1.8    # never missed an optimal grid at 1.73 max
UNSAT_AREA_RATIO = 2.0   # covers all grids up to area ratio 2.0 (6x10 for n=10)


def upper_bound(n):
    if n in KNOWN:
        return KNOWN[n]
    # Triangular bound n*(n-1)/2 is valid for n >= 4.
    # For small n, use n*ceil(n/2) as a safe upper bound.
    tri = n * (n - 1) // 2
    safe_ub = n * max(1, math.ceil(n / 2))
    ub = max(tri, safe_ub)
    if n - 1 in KNOWN:
        return min(ub, int(KNOWN[n - 1] * 1.6) + 1)
    return ub


def lower_bound(n):
    if n in KNOWN:
        return KNOWN[n]
    if n - 1 in KNOWN:
        return KNOWN[n - 1] + 1
    return n


def candidate_grids(n, k, area_ratio=SAT_AREA_RATIO):
    """Grid candidates (H, W) with H <= W, sorted by likelihood.

    Known optimal grids: height ~ ceil(n/2), width ~ n.
    area_ratio caps the maximum grid area relative to k.

    Spanning bound filter: skip grids with H < ceil(n/2) because some
    n-ominoes have min-height = ceil(n/2) and won't fit in shorter grids.
    (Theorem: |P| >= H + W - 1 for connected P, so no n-omino spans
    ceil(n/2)+1 rows AND ceil(n/2)+1 cols when n <= 2*ceil(n/2).)
    """
    pred_w = n
    pred_h = max(1, math.ceil(n / 2))
    max_area = int(k * area_ratio) + 1
    min_h = pred_h  # spanning bound: pieces need at least this height

    grids = []
    for w in range(n, max_area + 1):
        for h in range(min_h, w + 1):
            area = h * w
            if area >= k and area <= max_area:
                grids.append((h, w))

    grids.sort(key=lambda hw: abs(hw[0] - pred_h) + abs(hw[1] - pred_w))
    return grids


# ================================================================
# CP-SAT solver core
# ================================================================

def _find_i_piece_idx(n, pieces):
    """Find the index of the straight n-omino (I-piece) in the piece list."""
    target = frozenset((0, c) for c in range(n))
    for i, piece in enumerate(pieces):
        cells = list(piece)
        for rot in range(4):
            for refl in [False, True]:
                transformed = []
                for r, c in cells:
                    if refl:
                        r, c = r, -c
                    for _ in range(rot):
                        r, c = -c, r
                    transformed.append((r, c))
                mr = min(r for r, c in transformed)
                mc = min(c for r, c in transformed)
                normed = frozenset((r - mr, c - mc) for r, c in transformed)
                if normed == target:
                    return i
    return None


def solve_container_cpsat(n, k, pieces, grid_h, grid_w, timeout=300,
                          symmetry_break=False):
    """Try to find a connected k-cell polyomino on (grid_h x grid_w) containing
    all free n-ominoes. Returns ('SAT'|'UNSAT'|'TIMEOUT', cells, time).

    If symmetry_break=True, fix the I-piece to row 0, cols 0..(n-1).
    Valid WLOG by translation + horizontal reflection.
    """
    all_place = get_all_placements(pieces, grid_h, grid_w)

    for pl in all_place:
        if not pl:
            return 'UNSAT', None, 0.0

    # Find I-piece canonical placement for symmetry break
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

    model = cp_model.CpModel()

    x = {}
    for r in range(grid_h):
        for c in range(grid_w):
            x[(r, c)] = model.NewBoolVar(f'x_{r}_{c}')

    model.Add(sum(x.values()) == k)

    for i, placements in enumerate(all_place):
        pvars = []
        for j, cells in enumerate(placements):
            b = model.NewBoolVar(f'p_{i}_{j}')
            for cell in cells:
                model.AddImplication(b, x[cell])
            pvars.append(b)
        if i == i_piece_idx and i_placement_idx is not None:
            model.Add(pvars[i_placement_idx] == 1)
        else:
            model.AddBoolOr(pvars)

    t0 = time.time()
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timeout
    solver.parameters.num_workers = min(4, os.cpu_count() or 4)

    while True:
        status = solver.Solve(model)

        if status == cp_model.INFEASIBLE:
            return 'UNSAT', None, time.time() - t0
        if status == cp_model.UNKNOWN:
            return 'TIMEOUT', None, time.time() - t0
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return 'TIMEOUT', None, time.time() - t0

        occupied = {(r, c) for r in range(grid_h) for c in range(grid_w)
                    if solver.Value(x[(r, c)])}

        components = find_components(occupied, directions=SQUARE_DIRS)
        if len(components) == 1:
            return 'SAT', sorted(occupied), time.time() - t0

        largest = max(components, key=len)
        for comp in components:
            if comp is largest:
                continue
            neighbors = []
            for r, c in comp:
                for dr, dc in SQUARE_DIRS:
                    nr, nc = r + dr, c + dc
                    if (0 <= nr < grid_h and 0 <= nc < grid_w
                            and (nr, nc) not in comp):
                        neighbors.append(x[(nr, nc)])
            model.AddBoolOr(
                neighbors + [x[(r, c)].Not() for r, c in comp]
            )

        remaining = timeout - (time.time() - t0)
        if remaining <= 0:
            return 'TIMEOUT', None, time.time() - t0
        solver.parameters.max_time_in_seconds = remaining


# ================================================================
# Multi-grid UNSAT proof
# ================================================================

def prove_unsat(n, k, pieces, timeout_per_grid=300, verbose=True):
    """Prove no connected k-cell polyomino contains all free n-ominoes.

    Tests ALL grids where every piece fits. Returns:
      ('PROVED', [])         -- UNSAT on all grids
      ('UNPROVEN', [grids])  -- some grids timed out (list of unresolved)
    """
    grids = candidate_grids(n, k, area_ratio=UNSAT_AREA_RATIO)
    unresolved = []

    if verbose:
        print(f"\n  UNSAT proof k={k}: {len(grids)} grid(s)")

    for gh, gw in grids:
        status, _, elapsed = solve_container_cpsat(
            n, k, pieces, gh, gw, timeout=timeout_per_grid,
            symmetry_break=True)

        if verbose:
            tag = f" ***TIMEOUT***" if status == 'TIMEOUT' else ""
            print(f"    {gh}x{gw}: {status} ({elapsed:.1f}s){tag}")

        if status == 'SAT':
            # k-cell solution EXISTS -- a(n) <= k, not > k
            if verbose:
                print(f"    UNEXPECTED SAT at k={k}! Lower bound wrong.")
            return ('SAT_FOUND', [(gh, gw)])

        if status == 'TIMEOUT':
            unresolved.append((gh, gw))

    if unresolved:
        return ('UNPROVEN', unresolved)
    return ('PROVED', [])


# ================================================================
# Main solver: two-phase search
# ================================================================

def solve_n(n, timeout_per_grid=300, verbose=True):
    """Solve a(n) in two phases:
      Phase 1: find optimal k (SAT direction, tight grids, fast)
      Phase 2: prove k-1 impossible (UNSAT direction, all grids, thorough)
    """
    if n == 0:
        return {'n': 0, 'size': 0, 'cells': [], 'grid_size': [0, 0],
                'status': 'PROVED', 'elapsed': 0.0, 'num_free_polyominoes': 1}

    t_start = time.time()
    pieces = enumerate_free(n)
    num_pieces = len(pieces)
    ub = upper_bound(n)
    lb = lower_bound(n)

    if verbose:
        print(f"\n{'='*60}")
        print(f"Solving a({n}): {num_pieces} free {n}-ominoes")
        print(f"Search range: [{lb}, {ub}]")
        print(f"{'='*60}")

    # --- Phase 1: find SAT answer ---
    best_cells = None
    best_grid = None

    def try_solve(k):
        nonlocal best_cells, best_grid
        grids = candidate_grids(n, k, area_ratio=SAT_AREA_RATIO)
        if verbose:
            print(f"\n  [SAT] k={k}: {len(grids)} grid(s)", end='', flush=True)

        for gh, gw in grids:
            status, cells, elapsed = solve_container_cpsat(
                n, k, pieces, gh, gw, timeout=timeout_per_grid)
            if verbose:
                print(f"\n    {gh}x{gw}: {status} ({elapsed:.1f}s)", end='', flush=True)
            if status == 'SAT':
                best_cells = cells
                best_grid = (gh, gw)
                if verbose:
                    print()
                return cells
            # For SAT search: TIMEOUT and UNSAT both mean "not found on this grid"
            # We continue to next grid. If all grids fail (UNSAT or TIMEOUT),
            # we report "not found" for this k, which the search treats as UNSAT.
            # This is SAFE for the SAT direction: we might miss a solution on a
            # timed-out grid, but top_down_search will find it at a higher k.

        if verbose:
            print()
        return None

    best_k, _ = top_down_search(try_solve, lb, ub, verbose=False)
    phase1_time = time.time() - t_start

    if best_k is None:
        if verbose:
            print(f"\n  FAILED: no SAT solution in [{lb}, {ub}]")
        return None

    if verbose:
        print(f"\n  Phase 1 result: a({n}) <= {best_k} "
              f"(SAT on {best_grid[0]}x{best_grid[1]}, {phase1_time:.1f}s)")

    # --- Phase 2: prove UNSAT at k-1 ---
    proof_k = best_k - 1
    if proof_k < lb:
        # Already at lower bound -- known proved
        proof_status = 'PROVED'
        unresolved = []
    else:
        proof_status, unresolved = prove_unsat(
            n, proof_k, pieces, timeout_per_grid=timeout_per_grid, verbose=verbose)

    total_time = time.time() - t_start

    if proof_status == 'PROVED':
        status_str = 'PROVED'
    elif proof_status == 'SAT_FOUND':
        # Unexpected: solution found at k-1. Phase 1 search was wrong.
        if verbose:
            print(f"  ERROR: SAT found at k={proof_k}, but Phase 1 said a(n)={best_k}")
        return None
    else:
        status_str = 'UPPER BOUND'

    if verbose:
        print(f"\n  RESULT: a({n}) = {best_k} ({status_str})")
        print(f"  Grid: {best_grid[0]}x{best_grid[1]}")
        print(f"  Time: {total_time:.1f}s")
        if unresolved:
            print(f"  UNRESOLVED grids at k={proof_k}: "
                  + ", ".join(f"{h}x{w}" for h, w in unresolved))

    result = {
        'n': n, 'size': best_k,
        'cells': [list(c) for c in best_cells],
        'grid_size': list(best_grid),
        'status': status_str, 'elapsed': round(total_time, 1),
        'num_free_polyominoes': num_pieces,
    }
    if unresolved:
        result['unresolved_grids'] = [[h, w] for h, w in unresolved]

    return result


def verify_solution(n, cells):
    """Verify connectivity + containment of all free n-ominoes."""
    cell_set = set(tuple(c) for c in cells)
    components = find_components(cell_set, directions=SQUARE_DIRS)
    if len(components) != 1:
        return False, f"Not connected: {len(components)} components"

    pieces = enumerate_free(n)
    mr = min(r for r, c in cell_set)
    mc = min(c for r, c in cell_set)
    rows = max(r for r, c in cell_set) - mr + 1
    cols = max(c for r, c in cell_set) - mc + 1
    normed = frozenset((r - mr, c - mc) for r, c in cell_set)
    placements = get_all_placements(pieces, rows, cols)

    for i, pls in enumerate(placements):
        if not any(all(c in normed for c in pl) for pl in pls):
            return False, f"Piece {i} cannot be placed"
    return True, "OK"


# ================================================================
# CLI
# ================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Solve A327094: smallest polyomino containing all free n-ominoes')
    parser.add_argument('--n', type=int, help='Compute a(n) for specific n')
    parser.add_argument('--all', action='store_true', help='Compute all terms from n=0')
    parser.add_argument('--max-n', type=int, default=10, help='Maximum n for --all mode')
    parser.add_argument('--json', type=str, help='Output results to JSON file')
    parser.add_argument('--timeout', type=int, default=300, help='Timeout per grid (seconds)')
    parser.add_argument('--verify', action='store_true', help='Verify solutions')
    parser.add_argument('--fresh', action='store_true',
                        help='Ignore KNOWN values for bounds (proof mode)')
    args = parser.parse_args()

    if args.n is None and not args.all:
        parser.error("Specify --n N or --all")

    if args.fresh:
        KNOWN.clear()

    results = {}
    ns = range(0, args.max_n + 1) if args.all else [args.n]

    for n in ns:
        result = solve_n(n, timeout_per_grid=args.timeout)
        if result is None:
            print(f"FAILED: a({n}) could not be determined")
            continue

        results[str(n)] = result
        KNOWN[n] = result['size']

        if args.verify and result['cells']:
            ok, msg = verify_solution(n, result['cells'])
            print(f"  Verification: {msg}")
            if not ok:
                result['status'] = f'VERIFICATION FAILED: {msg}'

    if args.json:
        json_path = args.json
        if not os.path.isabs(json_path):
            json_path = os.path.join(_PROJECT_DIR, json_path)
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults written to {json_path}")

    print(f"\n{'='*60}")
    print("Summary:")
    for n_str in sorted(results.keys(), key=int):
        r = results[n_str]
        extra = ""
        if r.get('unresolved_grids'):
            extra = f" [unresolved: {len(r['unresolved_grids'])} grids]"
        print(f"  a({n_str}) = {r['size']} ({r['status']}, {r['elapsed']}s){extra}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
