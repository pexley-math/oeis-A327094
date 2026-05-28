# Proof certificates -- A327094

This directory holds the machine-checkable proof certificates behind the proved terms.
Each is an LRAT proof that any LRAT checker re-verifies with no project code and no
private libraries.

## Contents

Each proved term `n` (cell count `k = a(n) - 1`) ships one CNF / LRAT pair per
bounding-box window the proof covered, plus a shared sidecar:

| File | What it is |
|---|---|
| `nN_RxC_kK.cnf` | The CNF whose unsatisfiability proves no `k`-cell solution exists in an `R x C` window |
| `nN_RxC_kK.lrat` | The LRAT proof of that unsatisfiability |
| `nN_kK_relaxed_lrat.sidecar.json` | SHA-256 of the CNF / LRAT files plus the recorded verdict (shared across all windows of term `n`) |
| `certification-summary.json` | Per-term verdict summary across all terms |

## Verifying the Proof

Run any LRAT checker on a `.cnf` / `.lrat` pair, e.g.:

```
lrat-check n1_1x1_k0.cnf n1_1x1_k0.lrat
```

A `s VERIFIED` result confirms the proof. The matching sidecar carries the SHA-256
of both files and the verdict (`REFUTATION` for a lower-bound proof), so you can
confirm the artefacts have not drifted.

### Omitted certificates

These LRAT files exceed GitHub's 100 MB per-file limit and are not shipped: `n10_6x10_k30.lrat`.
Their `.cnf` and the shared sidecar (SHA-256 + verdict) are retained; regenerate the `.lrat`
with the check described in the root README "Verifying the Proof" section.
