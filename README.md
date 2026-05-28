# OEIS A327094 -- A327094: Smallest Polyomino Containing All Free n-Ominoes

Data, certificates, and figures for [OEIS A327094](https://oeis.org/A327094).

## The Problem

a(n) is the number of cells in the smallest polyomino that contains every free n-omino as a subshape under rotation, reflection, and translation.

## Animation

![Animation of the optimal construction](research/oeis-a327094-animation.gif)

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

This repository re-derives and re-certifies a(1..10) = 1, 2, 4, 6, 9, 12, 17, 20, 26, 31, matching the published OEIS data. The listed values are proved minimal among polyomino containers whose bounding box lies within the searched window (height at least ceil(n/2), width at least n, area at most twice the cell count). A smaller container with a more elongated bounding box outside that window is not separately excluded, so global minimality remains conjectural.

## Conjecture

Kagey conjectures a(11) = 37 and a(12) = 43 (UNVERIFIED). Our frontier search at n = 11 (17073 free pieces) exhausted resources before certifying a value, so these terms are neither confirmed nor refuted.

## Method

Each value is found by an exact container search that produces a minimal witness container (the upper bound), and the lower bound is established by an infeasibility proof over a finite bounding-box window. Every term is cross-checked by two independent verifiers -- a geometric containment check and a relaxed-infeasibility check on a different engine -- and carries a machine-checked refutation certificate. Minimality is proved within the search window (height at least ceil(n/2), width at least n, area at most twice the cell count); global minimality is conjectured.

## Verifying the Proof

Re-check any SAT-certified term with any LRAT proof checker -- no project code or private libraries required:

```bash
lrat-check research/certificates/n10_5x10_k30.cnf research/certificates/n10_5x10_k30.lrat
```

## Files

| File | Description |
|------|-------------|
| `research/solver-results.json` | Proved values with bounding boxes and per-term solver timing. |
| `research/solver-run-log.txt` | Solver run log (per-term search transcript). |
| `research/verify_method1-results.json` | Independent verifier results (one row per term). |
| `research/verify_method1-run-log.txt` | Independent verifier transcript. |
| `research/verify_method2-results.json` | Second independent verifier results (disjoint engine). |
| `research/verify_method2-run-log.txt` | Second independent verifier transcript. |
| `research/conjecture-report.md` | Conjecture search: subsequence matches, formula tests, near-misses. |
| `research/certificates/` | Per-term proof certificates (CNF + LRAT + sidecars) and a README with the lrat-check command. |
| `research/oeis-a327094-animation.gif` | Animation of the optimal construction. |
| `submission/oeis-a327094-figures.pdf` | Publication figures. |
| `submission/paper.pdf` | The paper (figures embedded): problem, construction, lower-bound proof, conjectures, and prior art. |
| `submission/paper.md` | The paper in markdown (same text as the PDF; renders in-browser). |

## Prior Art and Acknowledgments

A327094 was introduced by Peter Kagey (2019), who gave the upper bound a(n) <= n(n-1)/2 for n >= 4. The minimalist-container count is the companion sequence A352029 (John Mason, 2022).

This work was inspired by the [OEIS](https://oeis.org/) and the community of
contributors who maintain it.

## Hardware

AMD Ryzen 5 5600 (6-core / 12-thread), 16 GB RAM.

## License

[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) -- Peter Exley, 2026.

This work is freely available. If you find it useful, a citation or acknowledgment
is appreciated but not required.

## Links

- [A000105](https://oeis.org/A000105) -- number of free polyominoes with n cells (the pieces contained)
- [A327094](https://oeis.org/A327094) -- OEIS record (this sequence)
- [A352029](https://oeis.org/A352029) -- number of minimalist n-omino containers (containers achieving a(n))
- [A395422](https://oeis.org/A395422) -- analogous smallest polyiamond containing all fixed n-iamonds (triangular lattice)
