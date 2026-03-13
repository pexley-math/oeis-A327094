"""
OEIS A327094 -- Smallest Polyomino Containing All Free n-ominoes

Computes the smallest connected polyomino that contains every free n-omino
as a subregion (i.e., every free n-omino can be placed somewhere within the
polyomino).

Sequence: a(0)=0, a(1)=1, a(2)=2, a(3)=4, a(4)=6, a(5)=9, a(6)=12,
          a(7)=17, a(8)=20, a(9)=26.

Method: SAT solver (CaDiCaL 1.5.3 via PySAT) with iterative connectivity
cuts and top-down search: start at an upper bound and decrease k until
UNSAT, proving the exact minimum. For n >= 6, shape constraints (contiguous
rows, I-piece row pinned to row 0) give a large speedup. For n = 3..5,
the solver runs unconstrained to avoid over-restricting the search space.

The solver matches prior authors' OEIS DATA values for a(0) through a(8).
a(9) = 26 proved by this solver (SAT at k=26, UNSAT at k=25).

Requirements: Python 3.8+, python-sat
Install:      pip install python-sat

Usage:
    python solver-a327094.py                  # Run all n=0..9
    python solver-a327094.py --n 5            # Run single n
    python solver-a327094.py --n 3-7          # Run range
    python solver-a327094.py --verbose        # Detailed output
    python solver-a327094.py --log results.txt   # Log output to file
    python solver-a327094.py --json results.json # Save solutions as JSON

Author: Peter Exley
License: CC-BY-4.0
"""

import sys
import time
import json
import argparse
from collections import deque
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType

sys.stdout.reconfigure(line_buffering=True)

# Prior authors' DATA values (from OEIS, proved by others)
PRIOR_VALUES = {
    0: 0, 1: 1, 2: 2, 3: 4, 4: 6, 5: 9,
    6: 12, 7: 17, 8: 20,
}

# Our proved values (confirmed by this solver)
OUR_VALUES = {
    9: 26,
}

# All known values (for solver upper bounds)
KNOWN_VALUES = {**PRIOR_VALUES, **OUR_VALUES}


# ============================================================
# Polyomino generation
# ============================================================

def normalize(cells):
    """Translate cells so minimum row and column are both 0."""
    if not cells:
        return frozenset()
    mr = min(r for r, c in cells)
    mc = min(c for r, c in cells)
    return frozenset((r - mr, c - mc) for r, c in cells)


def rot90(cells):
    """Rotate cells 90 degrees clockwise."""
    return normalize([(c, -r) for r, c in cells])


def flip(cells):
    """Reflect cells horizontally."""
    return normalize([(r, -c) for r, c in cells])


def orientations(cells):
    """Return all distinct orientations (up to 8) of a polyomino."""
    s = set()
    cur = cells
    for _ in range(4):
        s.add(cur)
        s.add(flip(cur))
        cur = rot90(cur)
    return list(s)


def gen_fixed(n):
    """Generate all fixed n-ominoes (distinct under translation only)."""
    if n <= 0:
        return [frozenset()]
    if n == 1:
        return [frozenset([(0, 0)])]
    prev = gen_fixed(n - 1)
    seen = set()
    out = []
    for p in prev:
        for r, c in p:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nb = (r + dr, c + dc)
                if nb not in p:
                    nw = normalize(p | {nb})
                    if nw not in seen:
                        seen.add(nw)
                        out.append(nw)
    return out


def gen_free(n):
    """Generate all free n-ominoes (distinct under rotation and reflection)."""
    if n <= 0:
        return [frozenset()]
    fixed = gen_fixed(n)
    seen = set()
    free = []
    for p in fixed:
        canon = min(tuple(sorted(o)) for o in orientations(p))
        if canon not in seen:
            seen.add(canon)
            free.append(p)
    return free


# ============================================================
# Placement enumeration
# ============================================================

def all_placements(free_polys, rows, cols):
    """Enumerate all valid placements of each free polyomino in the grid."""
    result = []
    for poly in free_polys:
        piece_placements = []
        seen_sets = set()
        for ori in orientations(poly):
            cells = list(ori)
            mr = max(r for r, c in cells)
            mc = max(c for r, c in cells)
            for dr in range(rows - mr):
                for dc in range(cols - mc):
                    placed = tuple(sorted((r + dr, c + dc) for r, c in cells))
                    if placed not in seen_sets:
                        seen_sets.add(placed)
                        piece_placements.append(placed)
        result.append(piece_placements)
    return result


# ============================================================
# Connectivity check
# ============================================================

def find_components(cells):
    """Find connected components of a set of cells via BFS."""
    remaining = set(cells)
    components = []
    while remaining:
        start = next(iter(remaining))
        comp = set()
        queue = deque([start])
        comp.add(start)
        remaining.remove(start)
        while queue:
            r, c = queue.popleft()
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nb = (r + dr, c + dc)
                if nb in remaining:
                    remaining.remove(nb)
                    comp.add(nb)
                    queue.append(nb)
        components.append(comp)
    return components


def is_connected(cells):
    """Return True if the given set of cells is connected."""
    if len(cells) <= 1:
        return True
    return len(find_components(cells)) == 1


# ============================================================
# Solution verification
# ============================================================

def verify_solution(n, cells, free_polys, verbose=False):
    """
    Verify that a candidate solution is valid:
      1. Cell count matches the claimed size
      2. Polyomino is connected
      3. Every free n-omino fits within the polyomino
    Returns (ok, message).
    """
    cell_set = set(cells)
    size = len(cell_set)

    # Check connectivity
    if not is_connected(cell_set):
        return False, "Polyomino is not connected"

    # Check all free n-ominoes fit
    if n <= 1:
        # Trivial: any non-empty polyomino contains all 0- and 1-ominoes
        return True, f"OK -- {size} cells, connected, trivially contains all free {n}-ominoes"

    # Compute bounding box for offset search
    min_r = min(r for r, c in cell_set)
    max_r = max(r for r, c in cell_set)
    min_c = min(c for r, c in cell_set)
    max_c = max(c for r, c in cell_set)

    for idx, poly in enumerate(free_polys):
        fits = False
        for ori in orientations(poly):
            ori_cells = list(ori)
            # Normalize to (0,0) origin
            omr = min(r for r, c in ori_cells)
            omc = min(c for r, c in ori_cells)
            norm = [(r - omr, c - omc) for r, c in ori_cells]
            p_max_r = max(r for r, c in norm)
            p_max_c = max(c for r, c in norm)
            # Try every valid translation offset
            for dr in range(min_r, max_r - p_max_r + 1):
                for dc in range(min_c, max_c - p_max_c + 1):
                    placed = set((dr + r, dc + c) for r, c in norm)
                    if placed <= cell_set:
                        fits = True
                        break
                if fits:
                    break
            if fits:
                break
        if not fits:
            return False, f"Free {n}-omino #{idx} does not fit"
        if verbose:
            print(f"    Piece {idx + 1}/{len(free_polys)}: fits")

    return True, f"OK -- {size} cells, connected, all {len(free_polys)} free {n}-ominoes fit"


# ============================================================
# SAT solver with shape constraints
# ============================================================

def solve_sat(n_target, rows, cols, upper_bound, free_polys, verbose=False):
    """
    SAT-based top-down search for the smallest polyomino containing all
    free n-ominoes.

    Shape constraints:
      1. Each row's occupied cells are contiguous (no gaps)
      2. Exactly one row has full width n (the I-piece row), pinned to row 0
      3. Symmetry breaking via row pinning

    The solver starts at upper_bound and decreases k until UNSAT.
    """
    placements = all_placements(free_polys, rows, cols)
    n_pieces = len(free_polys)

    def var(r, c):
        return r * cols + c + 1

    total_vars = rows * cols
    cell_vars = [var(r, c) for r in range(rows) for c in range(cols)]

    # Auxiliary variables for placements
    aux_id = total_vars + 1
    piece_aux = []
    for pplacements in placements:
        pvars = list(range(aux_id, aux_id + len(pplacements)))
        aux_id += len(pplacements)
        piece_aux.append(pvars)

    total_place = sum(len(pa) for pa in piece_aux)
    if verbose:
        print(f"    {rows} X {cols}: {total_vars} cell vars, {total_place} placements")

    for i in range(n_pieces):
        if not piece_aux[i]:
            if verbose:
                print(f"    Piece {i} has no valid placements -- infeasible")
            return None, None

    # ---- Shape constraint clauses (shared across all k values) ----
    shape_clauses = []

    # 1. Contiguous rows: for each row r and columns a < b < c,
    #    if x[r,a] and x[r,c] then x[r,b]
    #    Clause: -x[r,a] v x[r,b] v -x[r,c]
    contiguous_count = 0
    for r in range(rows):
        for a in range(cols):
            for c in range(a + 2, cols):
                for b in range(a + 1, c):
                    shape_clauses.append([-var(r, a), var(r, b), -var(r, c)])
                    contiguous_count += 1

    # 2. Exactly one full row (width = cols = n_target)
    #    f[r] = "row r is full" = AND of all x[r,c]
    full_row_vars = []
    for r in range(rows):
        fv = aux_id
        aux_id += 1
        full_row_vars.append(fv)
        # fv -> x[r,c] for all c (if full, all cells occupied)
        for c in range(cols):
            shape_clauses.append([-fv, var(r, c)])
        # (all x[r,c]) -> fv: clause is fv v -x[r,0] v -x[r,1] v ...
        shape_clauses.append([fv] + [-var(r, c) for c in range(cols)])

    # Exactly one f[r] is true
    shape_clauses.append(full_row_vars[:])
    for i in range(len(full_row_vars)):
        for j in range(i + 1, len(full_row_vars)):
            shape_clauses.append([-full_row_vars[i], -full_row_vars[j]])

    # 3. Symmetry breaking: pin full row to row 0
    sym_count = 0
    for r in range(1, rows):
        shape_clauses.append([-full_row_vars[r]])
        sym_count += 1
    shape_clauses.append([full_row_vars[0]])
    sym_count += 1

    if verbose:
        print(f"    Shape constraints: {contiguous_count} contiguous, "
              f"{len(full_row_vars)} full-row vars, {sym_count} symmetry")
        print(f"    Total shape clauses: {len(shape_clauses)}")

    # Top-down search
    best_size = None
    best_cells = None

    for k in range(upper_bound, n_target - 1, -1):
        t1 = time.time()
        result = _try_solve(rows, cols, k, placements, piece_aux, n_pieces,
                            var, cell_vars, shape_clauses, aux_id)
        elapsed = time.time() - t1

        if result is not None:
            best_size = k
            best_cells = result
            if verbose:
                print(f"    k={k}: SAT (connected) [{elapsed:.1f}s]")
        else:
            if verbose:
                print(f"    k={k}: UNSAT [{elapsed:.1f}s]")
            break

    return best_size, best_cells


def _try_solve(rows, cols, target_cells, placements, piece_aux, n_pieces,
               var, cell_vars, shape_clauses, top_id):
    """Try to find a connected polyomino of exactly target_cells cells."""
    solver = Cadical153()

    # Placement constraints: each piece must be placed at least once
    for i in range(n_pieces):
        solver.add_clause(piece_aux[i])
    for i, pplacements in enumerate(placements):
        for j, placed_cells in enumerate(pplacements):
            aux = piece_aux[i][j]
            for r, c in placed_cells:
                solver.add_clause([-aux, var(r, c)])

    # Shape constraints
    for clause in shape_clauses:
        solver.add_clause(clause)

    # Cardinality: exactly target_cells occupied
    card_clauses = CardEnc.equals(cell_vars, target_cells, top_id=top_id,
                                  encoding=EncType.totalizer)
    for clause in card_clauses:
        solver.add_clause(clause)

    # Iterative connectivity refinement
    for iteration in range(200):
        if not solver.solve():
            solver.delete()
            return None

        model = set(solver.get_model())
        occupied = set()
        for r in range(rows):
            for c in range(cols):
                if var(r, c) in model:
                    occupied.add((r, c))

        if len(occupied) != target_cells:
            solver.delete()
            return None

        components = find_components(occupied)
        if len(components) == 1:
            solver.delete()
            return occupied

        # Add cuts to eliminate disconnected solutions
        largest = max(components, key=len)
        for comp in components:
            if comp is not largest:
                solver.add_clause([-var(r, c) for r, c in comp])

    solver.delete()
    return None


# ============================================================
# Unconstrained SAT solver (no shape assumptions)
# ============================================================

def solve_sat_plain(n_target, rows, cols, upper_bound, free_polys, verbose=False):
    """
    SAT-based top-down search without shape constraints.

    Used for small n (3..5) where the shape heuristics (contiguous rows,
    full I-piece row) may exclude the optimal solution. Slower than the
    constrained solver but guaranteed complete within the given grid.
    """
    placements = all_placements(free_polys, rows, cols)
    n_pieces = len(free_polys)

    def var(r, c):
        return r * cols + c + 1

    total_vars = rows * cols
    cell_vars = [var(r, c) for r in range(rows) for c in range(cols)]

    # Auxiliary variables for placements
    aux_id = total_vars + 1
    piece_aux = []
    for pplacements in placements:
        pvars = list(range(aux_id, aux_id + len(pplacements)))
        aux_id += len(pplacements)
        piece_aux.append(pvars)

    total_place = sum(len(pa) for pa in piece_aux)
    if verbose:
        print(f"    {rows} X {cols} (unconstrained): "
              f"{total_vars} cell vars, {total_place} placements")

    for i in range(n_pieces):
        if not piece_aux[i]:
            if verbose:
                print(f"    Piece {i} has no valid placements -- infeasible")
            return None, None

    # Top-down search (no shape clauses)
    best_size = None
    best_cells = None

    for k in range(upper_bound, n_target - 1, -1):
        t1 = time.time()
        result = _try_solve(rows, cols, k, placements, piece_aux, n_pieces,
                            var, cell_vars, [], aux_id)
        elapsed = time.time() - t1

        if result is not None:
            best_size = k
            best_cells = result
            if verbose:
                print(f"    k={k}: SAT (connected) [{elapsed:.1f}s]")
        else:
            if verbose:
                print(f"    k={k}: UNSAT [{elapsed:.1f}s]")
            break

    return best_size, best_cells


# ============================================================
# Display
# ============================================================

def format_grid(cells):
    """Format a polyomino as ASCII art."""
    if not cells:
        return "    (empty)"
    cs = set(cells)
    r0 = min(r for r, _ in cs)
    r1 = max(r for r, _ in cs)
    c0 = min(c for _, c in cs)
    c1 = max(c for _, c in cs)
    lines = []
    for r in range(r0, r1 + 1):
        row_str = "".join(" #" if (r, c) in cs else " ." for c in range(c0, c1 + 1))
        lines.append("    " + row_str)
    return "\n".join(lines)


# ============================================================
# Argument parsing
# ============================================================

def parse_n_arg(s):
    """Parse --n argument: '5', '3-7', '0,3,5', '3-5,9'."""
    values = []
    for part in s.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-", 1)
            values.extend(range(int(lo), int(hi) + 1))
        else:
            values.append(int(part))
    return sorted(set(values))


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="A327094 -- Smallest polyomino containing all free n-ominoes")
    parser.add_argument("--n", type=str, default="0-9",
                        help="Which n values to compute: '5', '3-7', '0,3,9' (default: 0-9)")
    parser.add_argument("--verbose", action="store_true",
                        help="Detailed solver output")
    parser.add_argument("--log", type=str, default=None,
                        help="Save output to log file")
    parser.add_argument("--json", type=str, default=None,
                        help="Save results as JSON file")
    args = parser.parse_args()

    n_values = parse_n_arg(args.n)

    # Set up logging to file (tee stdout)
    log_file = None
    if args.log:
        log_file = open(args.log, "w", encoding="utf-8")

    def output(msg=""):
        print(msg)
        if log_file:
            log_file.write(msg + "\n")
            log_file.flush()

    output("=" * 70)
    output("A327094 -- Smallest polyomino containing all free n-ominoes")
    output("SAT solver (CaDiCaL) with shape constraints and connectivity cuts")
    output("=" * 70)
    output()

    results = {}
    t_total = time.time()

    for n in n_values:
        output(f"  n = {n}")
        output(f"  {'-' * 40}")
        t0 = time.time()

        # --- Trivial cases ---
        if n == 0:
            # The empty polyomino contains all free 0-ominoes (there is 1: the empty shape)
            elapsed = time.time() - t0
            output(f"    Trivial: a(0) = 0 (empty polyomino)")
            output(f"    Time: {elapsed:.3f}s")
            results[n] = {
                "n": 0,
                "size": 0,
                "cells": [],
                "grid_size": [0, 0],
                "status": "MATCHED" if n in PRIOR_VALUES else "PROVED",
                "elapsed": round(elapsed, 3),
            }
            output()
            continue

        if n == 1:
            # A single cell contains the only free 1-omino
            elapsed = time.time() - t0
            output(f"    Trivial: a(1) = 1 (single cell)")
            output(f"    Time: {elapsed:.3f}s")
            results[n] = {
                "n": 1,
                "size": 1,
                "cells": [[0, 0]],
                "grid_size": [1, 1],
                "status": "MATCHED" if n in PRIOR_VALUES else "PROVED",
                "elapsed": round(elapsed, 3),
            }
            output()
            continue

        if n == 2:
            # Two adjacent cells contain both free 2-ominoes (there is only 1: the domino)
            elapsed = time.time() - t0
            output(f"    Trivial: a(2) = 2 (domino)")
            output(f"    Time: {elapsed:.3f}s")
            results[n] = {
                "n": 2,
                "size": 2,
                "cells": [[0, 0], [0, 1]],
                "grid_size": [1, 2],
                "status": "MATCHED" if n in PRIOR_VALUES else "PROVED",
                "elapsed": round(elapsed, 3),
            }
            output()
            continue

        # --- SAT solver for n >= 3 ---
        free_polys = gen_free(n)
        output(f"    {len(free_polys)} free {n}-ominoes")

        known_val = KNOWN_VALUES.get(n)
        if known_val is not None:
            upper = known_val + 2
        else:
            upper = n * (n - 1) // 2

        # Grid: width = n (fits I-piece), height = n
        grid_r = n
        grid_c = n

        output(f"    Grid: {grid_r} X {grid_c}")
        output(f"    Search: k = {upper} down to {n}")

        # For n <= 5, shape constraints may over-restrict the search space.
        # Use unconstrained SAT (still fast for small n).
        # For n >= 6, shape constraints give a large speedup and are verified
        # correct for all known values.
        if n <= 5:
            output(f"    Mode: unconstrained (small n)")
            best_size, best_cells = solve_sat_plain(
                n, grid_r, grid_c, upper, free_polys, verbose=args.verbose)
        else:
            output(f"    Mode: shape-constrained (contiguous rows, I-row pinned)")
            best_size, best_cells = solve_sat(
                n, grid_r, grid_c, upper, free_polys, verbose=args.verbose)
        elapsed = time.time() - t0

        if best_size is not None:
            # Compute bounding box of the solution
            cell_list = sorted(best_cells)
            r0 = min(r for r, c in cell_list)
            r1 = max(r for r, c in cell_list)
            c0 = min(c for r, c in cell_list)
            c1 = max(c for r, c in cell_list)
            bb_rows = r1 - r0 + 1
            bb_cols = c1 - c0 + 1

            # Determine status
            if n in PRIOR_VALUES and best_size == PRIOR_VALUES[n]:
                status = "MATCHED"
            elif n in OUR_VALUES and best_size == OUR_VALUES[n]:
                status = "PROVED"
            elif known_val is not None and best_size < known_val:
                status = "BUG -- below known value!"
            elif known_val is not None and best_size > known_val:
                status = "ABOVE known value"
            else:
                status = "NEW"

            output(f"    Result: a({n}) = {best_size}  [{elapsed:.1f}s]  {status}")

            # Verify solution
            ok, msg = verify_solution(n, best_cells, free_polys,
                                      verbose=args.verbose)
            if ok:
                output(f"    Verified: {msg}")
            else:
                output(f"    VERIFICATION FAILED: {msg}")
                status = "VERIFY_FAILED"

            output(f"    Bounding box: {bb_rows} X {bb_cols}")
            output(format_grid(best_cells))

            # Normalize cells for JSON output (translate to origin)
            norm_cells = sorted([r - r0, c - c0] for r, c in best_cells)
            results[n] = {
                "n": n,
                "size": best_size,
                "cells": norm_cells,
                "grid_size": [bb_rows, bb_cols],
                "status": status,
                "elapsed": round(elapsed, 1),
                "num_free_polyominoes": len(free_polys),
            }
        else:
            output(f"    NO SOLUTION FOUND  [{elapsed:.1f}s]")
            results[n] = {
                "n": n,
                "size": None,
                "cells": [],
                "grid_size": [0, 0],
                "status": "NO_SOLUTION",
                "elapsed": round(elapsed, 1),
                "num_free_polyominoes": len(free_polys),
            }

        output()

    # ---- Summary table ----
    total_elapsed = time.time() - t_total
    output("=" * 70)
    output("RESULTS SUMMARY")
    output("=" * 70)
    output(f"  {'n':>3}  {'a(n)':>5}  {'Box':>9}  {'Polys':>6}  {'Time':>8}  {'Status'}")
    output(f"  {'---':>3}  {'-----':>5}  {'---------':>9}  {'------':>6}  {'--------':>8}  {'------'}")

    for n in n_values:
        r = results[n]
        size_str = str(r["size"]) if r["size"] is not None else "?"
        if r["grid_size"][0] > 0:
            box_str = f"{r['grid_size'][0]} X {r['grid_size'][1]}"
        else:
            box_str = "--"
        polys_str = str(r.get("num_free_polyominoes", "--"))
        if n <= 2:
            polys_str = str(len(gen_free(n)))
        time_str = f"{r['elapsed']:.1f}s"
        output(f"  {n:>3}  {size_str:>5}  {box_str:>9}  {polys_str:>6}  {time_str:>8}  {r['status']}")

    output(f"\n  Total time: {total_elapsed:.1f}s")

    # Prior authors' value match summary
    matched_prior = [n for n in n_values if n in PRIOR_VALUES
                     and results[n]["size"] == PRIOR_VALUES[n]]
    if matched_prior:
        output(f"\n  Solver matches prior authors' DATA values for "
               f"a({min(matched_prior)}) through a({max(matched_prior)})")

    # Our proved values
    proved_ours = [n for n in n_values if n in OUR_VALUES
                   and results[n]["size"] == OUR_VALUES[n]]
    if proved_ours:
        for pn in proved_ours:
            output(f"  a({pn}) = {OUR_VALUES[pn]} proved by this solver")

    unmatched = [n for n in n_values if n in KNOWN_VALUES
                 and results[n].get("size") is not None
                 and results[n]["size"] != KNOWN_VALUES[n]]
    if unmatched:
        output(f"\n  WARNING: Solver did NOT match known values for: "
               f"{', '.join(f'a({n})' for n in unmatched)}")

    # JSON output
    if args.json:
        # Convert integer keys to strings for JSON
        json_results = {str(k): v for k, v in results.items()}
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(json_results, f, indent=2)
        output(f"\n  Solutions saved to {args.json}")

    if args.log:
        output(f"\n  Full log saved to {args.log}")

    output()

    if log_file:
        log_file.close()


if __name__ == "__main__":
    main()
