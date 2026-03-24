# OEIS A327094 -- Smallest Polyomino Containing All Free n-Ominoes

Solver code, data, and figures for [OEIS A327094](https://oeis.org/A327094).

## The Problem

a(n) = the minimum number of cells in a polyomino that contains all free
n-ominoes as subshapes. For example, a(5) = 9 means there exists a 9-cell
polyomino that contains every free pentomino, and no 8-cell polyomino can.

## Results

**Known terms (proved by prior authors):**

| n | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| a(n) | 0 | 1 | 2 | 4 | 6 | 9 | 12 | 17 | 20 |

**New proved terms (this work):**

| n | 9 | 10 |
|:---:|:---:|:---:|
| a(n) | 26 | 31 |

Both values proved by CP-SAT (OR-Tools) with CEGAR connectivity.
SAT solutions verified: connected polyomino, contains all free n-ominoes.
UNSAT proved on all spanning-bound-compatible grids, cross-validated with
CaDiCaL.

Conjectured: a(11) = 37, a(12) = 43.

## Conjecture

a(n) = floor((n+1)^2/4) + 1 for n >= 9, where floor((n+1)^2/4) =
[A002620](https://oeis.org/A002620)(n+1) (quarter-squares). The "staircase"
polyomino with row widths n, n-2, n-4, ... is optimal for small n but
requires one extra cell for n >= 9.

## Method

OR-Tools CP-SAT with CEGAR connectivity. Two-phase search: Phase 1 finds
the optimal k by SAT descent, Phase 2 proves k-1 impossible on all
candidate grids.

Key optimizations:
- **I-piece symmetry break:** fix straight n-omino to canonical position
  (4x UNSAT speedup)
- **Spanning bound grid filter:** skip grids with H < ceiling(n/2)
- **Cross-validation:** CaDiCaL confirms UNSAT without connectivity
  (stronger proof)

## Running the Solver

**Requirements:** Python 3.8+, ortools

```bash
pip install ortools

# Run all terms (takes ~35 minutes, a(10) dominates)
python code/solver-a327094.py --all --max-n 10 --fresh --verify --json research/solver-results.json

# Run specific term
python code/solver-a327094.py --n 9

# Cross-validate with CaDiCaL (requires pysat)
python code/drat-check.py --n 10 --k 30 --grid 5x10
```

## Files

| File | Description |
|------|-------------|
| `code/solver-a327094.py` | Main solver (CP-SAT + CEGAR connectivity) |
| `code/generate-figures.py` | Figure generation script |
| `code/drat-check.py` | CaDiCaL cross-validation |
| `code/exhaustive-unsat-cadical.py` | Extended grid coverage (117 grids) |
| `research/solver-results.json` | Machine-readable results with solution cells |
| `research/solver-run-log.txt` | Reviewer-grade proof of solver run |
| `submission/a327094-figures.pdf` | Publication figures (a(9), a(10)) |
| `submission/oeis-draft.txt` | OEIS submission text |

## Prior Art and Acknowledgments

The sequence A327094 was created by Peter Kagey (Sep 13 2019). Terms a(0)
through a(8) were proved by Peter Kagey. This work extends the sequence
with proved values a(9) = 26 and a(10) = 31.

This work was inspired by the [OEIS](https://oeis.org/) and the community
of contributors who maintain it.

## Hardware

AMD Ryzen 5 5600 (6-core / 12-thread), 16 GB RAM.

## License

[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) -- Peter Exley, 2026.

This work is freely available. If you find it useful, a citation or
acknowledgment is appreciated but not required.

## Links

- **OEIS page:** https://oeis.org/A327094
- **Quarter-squares (staircase lower bound):** https://oeis.org/A002620
