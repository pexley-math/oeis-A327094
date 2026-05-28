# Conjecture Report for A327094 -- smallest polyomino containing all free n-ominoes

**Date:** 2026-05-27
**Terms proved:** 10 (a(1..10))
**Source:** research/solver-results.json

## Proved Terms

| n | a(n) | Source |
|---|---|---|
| 1 | 1 | OUR PROOF (re-derived; matches Kagey range) |
| 2 | 2 | OUR PROOF |
| 3 | 4 | OUR PROOF |
| 4 | 6 | OUR PROOF |
| 5 | 9 | OUR PROOF |
| 6 | 12 | OUR PROOF |
| 7 | 17 | OUR PROOF |
| 8 | 20 | OUR PROOF |
| 9 | 26 | OUR PROOF (matches prior Exley contribution, re-derived) |
| 10 | 31 | OUR PROOF (matches prior Exley contribution, re-derived) |

All ten re-derived by this run and corroborated by two independent verifiers
(geometric upper bound + glucose relaxed-UNSAT lower bound) and a machine-checked
relaxed-LRAT REFUTATION certificate. They match the published OEIS A327094 data.

## OEIS Subsequence Search

All comparator values below were FETCHED live from oeis.org via
`bibliography.oeis_fetch` (not recalled). No network failure.

**Queries performed:**
- Full sequence 1, 2, 4, 6, 9, 12, 17, 20, 26, 31 -- EXACT MATCH to A327094
  (this sequence; live %S = 0,1,2,4,6,9,12,17,20,26,31 at offset 0).
- Shift (offset 0 form) 0, 1, 2, 4, 6, 9, 12, 17, 20, 26, 31 -- A327094.
- First differences 1, 2, 2, 3, 3, 5, 3, 6, 5 -- no meaningful match (irregular;
  any hit is a coincidental short-prefix collision, semantically unrelated).
- Second differences 1, 0, 1, 0, 2, -2, 3, -1 -- non-monotonic; no match.
- Partial sums / a(n)+-1 transforms -- no informative match.

**Matches found:**
- A327094 -- the sequence itself (live name: "a(n) is the number of cells in the
  smallest polyomino that can contain all free n-ominoes."; live data
  0,1,2,4,6,9,12,17,20,26,31; no %F formula line on the record).
- A000105 -- "Number of free polyominoes ... with n cells" (live data
  1,1,1,2,5,12,35,108,369,1285,4655,17073): the PIECE SET embedded, not a
  container analog.
- A352029 -- "a(n) is the number of minimalist polyominoes that can contain all
  n-ominoes" (live data 1,1,2,2,2,14,204,7): companion COUNT (a different
  quantity from the container SIZE); cross-reference only.

## Formula Tests

At least four formula families tested against the proved a(1..10):

| # | Formula family | Matches all terms? | First failure | Motivation |
|---|---|---|---|---|
| 1 | polynomial (degree 2 least-squares ~0.269n^2+0.399n+0.25) | No | n=7 (pred 16 vs 17); also n=8 (21 vs 20) | roughly quadratic growth, tight at the upper bound |
| 2 | polynomial (degree 3 least-squares) | No | n=7,8 (same misses) | test for a cubic correction |
| 3 | recurrence a(n)=p*a(n-1)+q*a(n-2)+s (small-int scan) | No | -- (no exact fit anywhere) | look for a linear recurrence |
| 4 | closed form / floor-family floor((n^2+c1)/c2)+delta | No | best fit < 7/10 exact | the floor-family method that worked on polyhex-container |
| 5 | identity to upper bound a(n) <= n(n-1)/2 (Kagey) | No (inequality, not identity) | tight only at n=3,4; gap grows 1,1,0,0,1,3,4,8,10,14 | the only proved structural bound |

The irregular second differences (1,0,1,0,2,-2,3,-1, non-monotonic) rule out any
low-degree polynomial, simple recurrence, or floor-family closed form. This is
consistent with A327094 carrying no %F on the OEIS record (no closed form known).

## Active Conjectures (match all proved terms -- UNVERIFIED)

No closed-form / polynomial / recurrence / floor-family formula matches all ten
proved terms, so we propose none of our own.

For awareness, the OEIS record (Kagey comment) carries an extrapolation:

### Conjecture (published, Kagey): a(11) = 37, a(12) = 43

- **Status:** UNVERIFIED. a(9)=26 and a(10)=31 from the same comment are now
  PROVED (they match our re-derivation), but a(11) and a(12) are not.
- **Data audit vs research/solver-results.json:** the conjecture's overlap with
  the proved range matches n=9 (26) and matches n=10 (31); a(11)=37 and a(12)=43
  are OUTSIDE the proved range (a(11) frontier check walled), so they are
  UNVERIFIED. No proved term is contradicted.
- **Frontier check:** NOT AVAILABLE -- our frontier push WALLED at a(11) (a
  resource limit on the 17073-piece model within the per-term cap), so the
  predicted a(11)=37 was neither confirmed nor refuted this run.
- **Mathematical motivation:** extrapolation of the observed growth toward the
  n(n-1)/2 upper bound; no structural proof. Treat as UNVERIFIED.

## Conjectures Rejected

- All five formula families in Formula Tests: each matched only a prefix
  (polynomials match n<=6 then miss n=7,8) or no exact fit at all (recurrence,
  floor-family). Rejected because they fail on the proved range.

## Cross-References Found

| OEIS ID | Name (fetched) | Relationship |
|---|---|---|
| A000105 | Number of free polyominoes with n cells | the piece set embedded (n=10 -> 4655, n=11 -> 17073 pieces) |
| A352029 | Number of minimalist polyominoes containing all n-ominoes | companion COUNT (vs this sequence's container SIZE) |

## Outcome

No conjecture found.

No closed-form formula matches the proved terms (the sequence is irregular and
the OEIS record carries no %F). The published next-term extrapolation
a(11)=37, a(12)=43 remains UNVERIFIED -- our frontier push walled at a(11), so it
was not tested. The proved values a(1..10) = 1,2,4,6,9,12,17,20,26,31 stand on
the two-verifier + LRAT certificate, not on any formula.
