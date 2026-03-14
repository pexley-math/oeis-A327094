# OEIS A327094 -- Smallest Polyomino Containing All Free n-ominoes

Solver code, data, and figures for [OEIS A327094](https://oeis.org/A327094).

## The Problem

a(n) = the number of cells in the smallest polyomino that can contain all free
n-ominoes. Each free n-omino must fit inside the container individually (not all
at once) via translation, rotation, or reflection.

## Results

| n | a(n) | Status |
|---|------|--------|
| 0 | 0 | Known (DATA) |
| 1 | 1 | Known (DATA) |
| 2 | 2 | Known (DATA) |
| 3 | 4 | Known (DATA) |
| 4 | 6 | Known (DATA) |
| 5 | 9 | Known (DATA) |
| 6 | 12 | Known (DATA) |
| 7 | 17 | Known (DATA) |
| 8 | 20 | Known (DATA) |
| 9 | **26** | **Proved by this solver** |

a(0)-a(8) from prior authors. **a(9) = 26 proved by this solver** (SAT at k=26,
UNSAT at k=25).

## Method

Exact SAT solver using PySAT/CaDiCaL. Boolean variables for cell occupancy on
an n X n grid, with auxiliary variables for each valid placement of each free
n-omino. Shape constraints (contiguous rows, exactly one full row of width n,
symmetry breaking) reduce the search space. Top-down search from upper bound
proves optimality.

## Running the Solver

**Requirements:** Python 3.8+, python-sat

```bash
pip install python-sat

# Run all terms n=0..9
python code/solver-a327094.py

# Run specific values
python code/solver-a327094.py --n 9
python code/solver-a327094.py --n 3-9

# Save results as JSON with log file
python code/solver-a327094.py --json results.json --verbose --log run.txt
```

## Files

| File | Description |
|------|-------------|
| `code/solver-a327094.py` | Unified SAT solver (all terms) |
| `code/generate-figures.py` | Figure generator (reads JSON, outputs Typst) |
| `research/solver-results.json` | Machine-readable results |
| `research/solver-run-log.txt` | Full solver output log |
| `submission/a327094-figures.pdf` | Solution figure for a(9) |

## Prior Art and Acknowledgments

The sequence A327094 was created by Peter Kagey (2019). Terms a(0) through
a(8) were proved by Peter Kagey. This work proves the next term a(9) = 26
using SAT.

This work was inspired by the [OEIS](https://oeis.org/) and the community of
contributors who maintain it.

## Hardware

AMD Ryzen 5 5600 (6-core), 16 GB RAM.

## License

[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) -- Peter Exley, 2026.

This work is freely available. If you find it useful, a citation or acknowledgment
is appreciated but not required.

## Links

- **OEIS page:** https://oeis.org/A327094
