# OEIS A327094: Smallest Polyomino Containing All Free n-Ominoes

**a(n)** = minimum number of cells in a polyomino that contains all free n-ominoes as subshapes.

## Known Terms

| n | a(n) | Grid | Pieces | Time | Author |
|---|------|------|--------|------|--------|
| 0 | 0 | -- | 1 | 0.0s | Peter Kagey |
| 1 | 1 | 1x1 | 1 | 0.0s | Peter Kagey |
| 2 | 2 | 1x2 | 1 | 0.0s | Peter Kagey |
| 3 | 4 | 2x3 | 2 | 0.0s | Peter Kagey |
| 4 | 6 | 2x4 | 5 | 0.0s | Peter Kagey |
| 5 | 9 | 3x5 | 12 | 0.1s | Peter Kagey |
| 6 | 12 | 3x6 | 35 | 0.5s | Peter Kagey |
| 7 | 17 | 4x7 | 108 | 4.5s | Peter Kagey |
| 8 | 20 | 4x8 | 369 | 10.8s | Peter Kagey |
| 9 | 26 | 5x9 | 1285 | 124s | Peter Exley |
| 10 | 31 | 5x10 | 4655 | 1952s | Peter Exley |

Conjectured: a(11) = 37, a(12) = 43.

## Method

OR-Tools CP-SAT with CEGAR connectivity. Two-phase search:
- **Phase 1 (SAT):** Binary + linear descent to find optimal k
- **Phase 2 (UNSAT):** Prove k-1 impossible on all candidate grids

Key optimisations:
- I-piece symmetry break (4x UNSAT speedup)
- Spanning bound grid filter (H >= ceil(n/2))
- Cross-validated with CaDiCaL via PySAT

## Conjecture

a(n) = floor((n+1)^2/4) + 1 for n >= 9, where floor((n+1)^2/4) = A002620(n+1) (quarter-squares). The "staircase" polyomino with row widths n, n-2, n-4, ... is optimal for small n but requires one extra cell for n >= 9.

## Files

```
code/
  solve_a327094.py          -- Main solver (CP-SAT + CEGAR)
  generate_figures.py       -- Figure generation script
  drat_check.py             -- CaDiCaL cross-validation
  exhaustive_unsat_cadical.py -- Extended grid coverage
research/
  solver-results.json       -- Proved terms with solution cells
  solver-run-log.txt        -- Reviewer-grade computation log
  conjecture-report.md      -- Formula analysis
submission/
  a327094-figures.pdf       -- Publication figures (a(9), a(10))
  oeis-draft.txt            -- OEIS submission text
  oeis-copy-helper.html     -- Click-to-copy for OEIS web form
```

## License

CC-BY-4.0. See [LICENSE](LICENSE).

## Links

- [OEIS A327094](https://oeis.org/A327094)
- [OEIS A002620](https://oeis.org/A002620) (quarter-squares, staircase lower bound)
