**Exact Minimal Polyomino Containers for All Free n-Ominoes: A327094 Through n = 10**

Peter Exley, Independent Researcher, Brisbane, Australia (pexley-math@github)
Submitted: May 27 2026

# Abstract

For each n, let a(n) be the number of cells in the smallest polyomino that
contains every free n-omino as a subshape under rotation, reflection, and
translation. This is OEIS A327094 (Peter Kagey, 2019). We re-derive a(1) through
a(10) = 1, 2, 4, 6, 9, 12, 17, 20, 26, 31 by exact constraint search: a
constraint solver finds a minimal container as a witness (the upper bound), and
proves no smaller container exists (the lower bound). Each value is corroborated
by two independent verifiers -- a pure-Python geometric containment check and a
relaxed-unsatisfiability check on a different SAT engine -- and by a
machine-checked LRAT refutation certificate. The lower bounds are established
over a finite search window: the listed values are proved minimal among
containers whose bounding box lies within the searched window (height at least
ceil(n/2), width at least n, area at most twice the cell count); a smaller
container with a more elongated bounding box outside that window is not
separately excluded, so global minimality remains conjectural. The sequence is
irregular -- its second differences are non-monotonic -- and admits no
closed-form, polynomial, or low-order recurrence fit over the proved range. The
published extrapolation a(11) = 37, a(12) = 43 (Kagey) remains unverified; our
frontier search at n = 11 (17073 free pieces) exhausted resources before
certifying a value.

**Keywords:** polyomino, universal container, exact cover, SAT solving, LRAT certificate, OEIS A327094

**MSC 2020:** 05B50, 05A15, 68R05

## Introduction

A free n-omino is a connected shape of n unit cells on the square lattice,
counted up to rotation and reflection. There are 1, 1, 2, 5, 12, 35, 108, 369,
1285, 4655 free n-ominoes for n = 1 through 10 (OEIS A000105). Call a polyomino a
*container* for size n if every free n-omino fits inside it under some rotation,
reflection, and translation. A327094 records a(n), the fewest cells such a
container can have. Peter Kagey introduced the sequence in 2019 and gave the
upper bound a(n) <= n(n-1)/2 for n >= 4, witnessed by a right-triangular
staircase.

This is a minimisation over an exponentially growing piece set, so exact values
are hard to reach: a(10) must simultaneously accommodate all 4655 decominoes. We
re-derive the published terms and certify them to current standard.

> **Theorem 1.** For n = 1 through 10, a(n) = 1, 2, 4, 6, 9, 12, 17, 20, 26, 31.
> Each value is the minimum cell count over all containers whose bounding box
> lies within the search window (height at least ceil(n/2), width at least n,
> area at most twice the cell count). Equivalently, a container of a(n) cells
> exists and no container of a(n) - 1 cells exists within that window.

The scope is honest: a hypothetical smaller container with a bounding box more
elongated than the window is not separately excluded, so global minimality
beyond the window remains conjectural. Within the window the values are exact.

**Contributions.**
- Re-derivation of a(1..10) on the current shared solver framework, matching the
  published OEIS data.
- Three independent corroborations per term: a geometric upper-bound verifier, a
  relaxed-unsatisfiability lower-bound verifier on a disjoint SAT engine, and a
  machine-checked LRAT refutation certificate.
- An empirical analysis showing the sequence resists closed-form, polynomial,
  and low-order recurrence fits, consistent with the absence of any formula on
  the OEIS record.
- A documented frontier wall at n = 11 (17073 pieces), leaving the published
  conjecture a(11) = 37 unverified.

## Definitions and Notation

We work on the square lattice Z^2 with 4-neighbour (edge) adjacency. A cell is a
lattice point (r, c). A polyomino is a finite, edge-connected set of cells. The
dihedral group D4 (four rotations and four reflections, eight elements) acts on
polyominoes; two polyominoes are the same *free* polyomino when one is a D4 image
of a translate of the other.

A polyomino C *contains* a free n-omino P if some D4 image of P, translated, is a
subset of C. C is a *container* for size n if it contains every free n-omino. The
sequence value a(n) is the minimum cell count of a container for size n. The
trivial terms are a(1) = 1 (one monomino, one cell) and a(2) = 2 (one domino, two
cells).

For a candidate cell count k we search a finite set of bounding boxes (the
*window*): boxes of height h and width w with h >= ceil(n/2) (a container must
span the straight n-omino in its short direction), w >= n (it must span the
straight n-omino lengthwise), and k <= h*w <= 2k. The height and width bounds are
proved; the area cap is the conditional element of the scope.

## Computational Methodology

For each n we search top-down from the upper bound max(n(n-1)/2, n+1). For a
candidate k we ask whether a connected k-cell container exists. The last feasible
k is a(n): a witness at k = a(n) gives the upper bound, and unsatisfiability at
k = a(n) - 1 gives the lower bound.

The search uses OR-Tools CP-SAT to find the witness (fast on this packing
structure) and proves the lower bound by an incremental CaDiCaL relaxed-cover
refutation with piece-driven counterexample-guided refinement: it shows that no
k-cell subset of any window grid -- connected or not -- can hold every piece.
Because a valid container must be connected, "no k-cell subset works" is strictly
stronger than "no connected k-cell container works", so the relaxed refutation
establishes the lower bound and does not depend on connectivity reasoning.

Verification is independent and threefold. A pure-Python geometric verifier
re-enumerates the free n-ominoes from scratch (no shared enumeration code) and
checks by direct set inclusion that the reported container holds every piece;
this certifies the upper bound. A second verifier re-runs the relaxed-cover
refutation on the glucose SAT engine -- a different engine from the solver's
CaDiCaL lower bound -- certifying the lower bound through disjoint code. Finally,
the lower bound is emitted as an LRAT refutation proof and validated by the
external lrat-check tool, giving a machine-checked certificate. Ablation of each
search heuristic (symmetry breaking, lonely-cell clauses, the translation
breaker) leaves every value unchanged, confirming the heuristics prune without
affecting the result. Full verification details are in the project's
verification report.

## Proved Values

Each value below is read from the solver output. The third column shows Kagey's
upper bound n(n-1)/2 for comparison; it is tight only at n = 3 and n = 4 and
loosens thereafter.

| n | a(n) | n(n-1)/2 |
|---|------|----------|
| 1 | 1 | 0 |
| 2 | 2 | 1 |
| 3 | 4 | 3 |
| 4 | 6 | 6 |
| 5 | 9 | 10 |
| 6 | 12 | 15 |
| 7 | 17 | 21 |
| 8 | 20 | 28 |
| 9 | 26 | 36 |
| 10 | 31 | 45 |

All ten terms are PROVED within the search window and carry an LRAT refutation
certificate with verdict REFUTATION, plus agreement from both independent
verifiers. The values match the published OEIS A327094 data; a(9) and a(10) were
first contributed to OEIS by the present author in March 2026 and are here
re-derived and re-certified.

## Empirical Analysis and Conjectures

The sequence grows roughly quadratically but irregularly. Its first differences
are 1, 2, 2, 3, 3, 5, 3, 6, 5 and its second differences are 1, 0, 1, 0, 2, -2,
3, -1 -- non-monotonic, with a drop at n = 7 to 8. This irregularity rules out a
simple description, and we confirmed it: a least-squares quadratic
(approximately 0.269 n^2 + 0.399 n + 0.25) matches n <= 6 but misses n = 7 (16
versus 17) and n = 8 (21 versus 20); a degree-three fit fails identically; a
small-integer linear recurrence a(n) = p a(n-1) + q a(n-2) + s has no exact
solution; and a floor-family form floor((n^2 + c)/d) + delta fits fewer than
seven of the ten terms for every small c and d. The OEIS record carries no
formula, consistent with these findings.

The published extrapolation a(11) = 37, a(12) = 43 (Kagey, in a comment on the
OEIS record) remains **UNVERIFIED**. Its overlap with our proved range matches
n = 9 and n = 10; n = 11 and n = 12 lie beyond it. Our frontier search at n = 11,
which must place all 17073 free undecominoes, exhausted resources before
certifying a value, so a(11) = 37 was neither confirmed nor refuted.

The companion sequence A352029 (John Mason, 2022) counts the minimalist
containers rather than measuring their size; it is a distinct quantity and is
referenced only for context.

## Discussion and Open Problems

The frontier sits at n = 10. The barrier is the piece count: A000105 jumps from
4655 at n = 10 to 17073 at n = 11, and the resulting model exceeded available
memory within the per-term budget. Reaching a(11) likely needs a more compact
encoding of the placement constraints or a decomposition that avoids materialising
all 17073 pieces at once.

Two questions stay open. First, whether any a(n) admits a closed form: the
evidence here is negative over n <= 10, but ten irregular terms cannot exclude a
formula that only becomes visible later. Second, whether the within-window
minimality proved here equals global minimality. The window's height and width
bounds are proved necessary; only the area cap is assumed. Proving that no
minimal container has a bounding box more elongated than the cap -- or exhibiting
one that does -- would settle the scope.

## Reproducibility

This section names the specific tools we used and what each one establishes,
so a reader can repeat the proof rather than take it on trust. The solver
and verifier source depend on a private shared library and are not
shipped, but the proof artefacts they produce are self-checking with
off-the-shelf tools.

**What we used, and what it proves.**

- *Witness search (upper bound).* OR-Tools CP-SAT finds, for each n, a
  connected k-cell container that holds every free n-omino with k = a(n).
  Existence of this witness is the upper bound a(n) <= k.
- *Infeasibility proof (lower bound).* CaDiCaL is run incrementally on
  the relaxed-cover CNF (the placement constraints without the
  connectivity requirement) at k = a(n) - 1, with piece-driven CEGAR
  refinement. UNSAT on the relaxed problem implies UNSAT on the
  connected problem, so this establishes a(n) >= k + 1 = a(n).
- *Machine-checked refutation certificate.* CaDiCaL emits an LRAT proof
  of the UNSAT verdict for each (n, k) and bounding-box window. We run
  the reference checker lrat-check on every emitted .cnf / .lrat pair;
  a `s VERIFIED` result is a third-party, code-free check that the
  refutation is correct.
- *First independent verifier (geometric upper bound).* A pure-Python
  geometric verifier re-enumerates the free n-ominoes from scratch
  (Redelmeier traversal, no shared code with the solver) and confirms
  by direct set inclusion that the reported witness contains every
  piece under some rotation / reflection / translation. This is an
  algorithmic check of the upper bound disjoint from the SAT search.
- *Second independent verifier (disjoint-engine lower bound).* A second
  verifier re-builds the same relaxed-cover CNF and re-runs the
  infeasibility proof on the glucose SAT engine instead of CaDiCaL.
  Agreement of two different SAT engines on UNSAT closes the
  "engine-bug" failure mode for the lower bound.

**What ships in this repository.** The CNF / LRAT pairs and their
shared sidecar (with SHA-256 and verdict) live under
`research/certificates/`, with a small README naming the one-line
checker command. The first and second verifier results + run logs ship
under `research/`. The solver and verifier source are not shipped (they
import the private shared library and would not run standalone), but
the certificates do not need them: any LRAT checker re-verifies any
shipped (.cnf, .lrat) pair with no project code at all, e.g.

```
lrat-check research/certificates/n10_5x10_k30.cnf \
           research/certificates/n10_5x10_k30.lrat
```

A `s VERIFIED` line confirms the lower-bound proof for that term and
window.

## Acknowledgements

We thank Peter Kagey for defining A327094, contributing its first terms, and
stating the upper bound a(n) <= n(n-1)/2 used as the search ceiling.

## Bibliography

- Kagey, P. (2019). "A327094: Smallest polyomino containing all free n-ominoes." The On-Line Encyclopedia of Integer Sequences. https://oeis.org/A327094
- Mason, J. (2022). "A352029: Number of minimalist polyominoes that can contain all n-ominoes." The On-Line Encyclopedia of Integer Sequences. https://oeis.org/A352029
- Redelmeier, D. H. (1981). "Counting Polyominoes: Yet Another Attack." *Discrete Mathematics* 36, 191-203.
- Sloane, N. J. A. "A000105: Number of free polyominoes (or square animals) with n cells." The On-Line Encyclopedia of Integer Sequences. https://oeis.org/A000105
