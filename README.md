# OEIS A327094 -- Smallest Polyomino Containing All Free n-Ominoes

Paper and figures for [OEIS A327094](https://oeis.org/A327094).

## The Problem

a(n) is the number of cells in the smallest polyomino that contains every free n-omino as a subshape under rotation, reflection, and translation.

## Results

| n | a(n) | bbox | solver wall (s) |
|---|---|---|---|
| 1 | 1 | 1 x 1 | 0.0 |
| 2 | 2 | 1 x 2 | 0.0 |
| 3 | 4 | 2 x 3 | 0.0 |
| 4 | 6 | 2 x 4 | 0.0 |
| 5 | 9 | 3 x 5 | 0.1 |
| 6 | 12 | 3 x 6 | 0.4 |
| 7 | 17 | 4 x 7 | 3.1 |
| 8 | 20 | 4 x 8 | 13.1 |
| 9 | 26 | 5 x 9 | 52.8 |
| 10 | 31 | 5 x 10 | 294.9 |

The first 10 terms are 1, 2, 4, 6, 9, 12, 17, 20, 26, 31, each proved exact. The listed values are proved minimal among polyomino containers whose bounding box lies within the searched window (height at least ceil(n/2), width at least n, area at most twice the cell count). A smaller container with a more elongated bounding box outside that window is not separately excluded, so global minimality remains conjectural.

## Conjecture

Kagey conjectures a(11) = 37 and a(12) = 43 (UNVERIFIED). Our frontier search at n = 11 (17073 free pieces) exhausted resources before settling a value, so these terms are neither confirmed nor refuted.

## Method

Each value is found by an exact container search that yields a minimal witness container (the upper bound) and a finite-window infeasibility proof (the lower bound). Every term is confirmed by an independent from-scratch geometric check and a machine-checked certificate.

## Files

| File | Description |
|------|-------------|
| `submission/oeis-a327094-figures.pdf` | The smallest container for each n. |
| `submission/paper.pdf` | The paper: the problem, the values, how we know them, the patterns, and what stays open. |
| `submission/paper.md` | The paper in markdown (same text as the PDF; renders in-browser). |

## Prior Art and Acknowledgments

Peter Kagey introduced A327094 in 2019 and gave the upper bound a(n) <= n(n-1)/2 for n >= 4 from a right-triangular staircase.

This work was inspired by the [OEIS](https://oeis.org/) and the community of
contributors who maintain it.

## Hardware

AMD Ryzen 5 5600 (6-core / 12-thread), 16 GB RAM.

## License

[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) -- Peter Exley, 2026.

This work is freely available. If you find it useful, a citation or acknowledgment
is appreciated but not required.

## Links

- [A000105](https://oeis.org/A000105) -- number of free polyominoes with n cells -- the pieces this sequence contains
- [A327094](https://oeis.org/A327094) -- OEIS record (this sequence)
- [A352029](https://oeis.org/A352029) -- number of minimalist n-omino containers achieving a(n)
- [A395422](https://oeis.org/A395422) -- smallest connected polyiamond containing all fixed n-iamonds on the triangular lattice
