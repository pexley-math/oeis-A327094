# Smallest Polyomino Containing Every Free n-Omino: A327094 for n up to 10

*Peter Exley, Independent Researcher, Brisbane, Australia (pexley-math@github). Submitted: May 27 2026.*

Pick a size `n` and write down every free `n`-omino -- every connected shape of
`n` squares, counted once per rotation and reflection. Now ask for the smallest
single polyomino that hides every one of those shapes somewhere inside it. The
number of cells in that smallest universal container is `a(n)`, and this note
pins down `a(1)` through `a(10)`.

## The problem

A free `n`-omino is a connected set of `n` unit cells on the square grid, taken
up to rotation and reflection. There are `1, 1, 2, 5, 12, 35, 108, 369, 1285,
4655` of them for `n = 1` through `10`. Call a polyomino a *container* for size
`n` if every free `n`-omino fits inside it under some rotation, reflection, and
translation. We want `a(n)`, the fewest cells a container for size `n` can have.
This is OEIS A327094 (Peter Kagey, 2019), who gave an upper bound from a
right-triangular staircase:

$$a(n) \le \frac{n(n-1)}{2} \quad (n \ge 4).$$

The values listed here are proved minimal among containers whose bounding box
lies within a searched window: height at least `ceil(n/2)`, width at least `n`,
and area at most twice the cell count. A smaller container with a more elongated
bounding box outside that window is not separately excluded, so global minimality
stays conjectural. Within the window the values are exact.

## Definitions

We work on the square lattice with edge (4-neighbour) adjacency; a cell is a
position `(r, c)`. A *polyomino* is a finite, edge-connected set of cells. The
dihedral group `D4` (four rotations and four reflections) acts on polyominoes;
two polyominoes are the same *free* polyomino when one is a `D4` image of a
translate of the other.

A polyomino `C` *contains* a free `n`-omino `P` when some `D4` image of `P`,
translated, is a subset of `C`. `C` is a *container* for size `n` when it contains
every free `n`-omino. Then `a(n)` is the smallest cell count of such a container.
The first two terms are immediate: `a(1) = 1` (the single monomino) and `a(2) =
2` (the single domino).

A candidate container of `k` cells is sought inside a finite set of bounding
boxes, the *window*: boxes of height `h` and width `w` with

$$h \ge \left\lceil \tfrac{n}{2} \right\rceil, \qquad w \ge n, \qquad k \le h\,w \le 2k.$$

The height and width bounds are forced -- a container must span the straight
`n`-omino both ways -- so the area cap is the one assumption that makes the
result conditional.

## The values

**Result.** For `n = 1` through `10`,

| `n`    | 1 | 2 | 3 | 4 | 5 | 6  | 7  | 8  | 9  | 10 |
| :--:   | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: |
| `a(n)` | 1 | 2 | 4 | 6 | 9 | 12 | 17 | 20 | 26 | 31 |

Each value is the smallest cell count over all containers whose bounding box lies
within the window above: a container of `a(n)` cells exists, and no container of
`a(n) - 1` cells exists within that window. Kagey's bound `n(n-1)/2` is tight only
at `n = 3` and `n = 4` and loosens after that (`45` against `31` at `n = 10`).

The smallest container achieving each value is drawn in the figure gallery,
[`figure.pdf`](figure.pdf). The shapes grow chunkier
as `n` rises: from almost a single fat row at small `n`, through the cross at
`n = 5` that first bulges out of one row to swallow the plus-pentomino, to the
thick staircase at `n = 10` that absorbs the most contorted decominoes.

## How we know

Each term needs an upper bound and a matching lower bound. We search top-down from
Kagey's ceiling. For a candidate `k` we ask whether a connected `k`-cell container
exists; the last `k` that answers yes is `a(n)`.

A constraint solver supplies the upper bound: for each `n` it finds an explicit
`a(n)`-cell container that holds all of the free `n`-ominoes at once. That witness
is a concrete shape, so the upper bound needs no trust in the solver.

A SAT solver supplies the lower bound by refutation. At `k = a(n) - 1` it proves
that no `k`-cell subset of any window grid -- connected or not -- can hold every
piece, using piece-driven counterexample-guided refinement to add only the clauses
that matter. Dropping the connectivity requirement only makes the problem easier,
so "no `k`-cell subset works" is strictly stronger than "no connected `k`-cell
container works"; the lower bound follows without any connectivity argument.

The values are confirmed two independent ways. A from-scratch geometric check
re-enumerates the free `n`-ominoes with its own code and confirms by direct set
inclusion that the reported container really holds every one -- an algorithmic
check of the upper bound that shares nothing with the search. And the refutation
is replayed as a machine-checked certificate and re-run on a second, unrelated SAT
engine, so the lower bound does not rest on one solver being bug-free. Removing
each search heuristic in turn (symmetry breaking, lonely-cell clauses, the
translation breaker) leaves every value unchanged, so the heuristics only prune
the search and never steer the answer.

## Patterns and open questions

The sequence grows roughly quadratically but never smoothly. Its first
differences are `1, 2, 2, 3, 3, 5, 3, 6, 5` and its second differences are `1, 0,
1, 0, 2, -2, 3, -1`, dropping back at `n = 7` to `8`. That irregularity is real,
not noise. A least-squares quadratic,

$$a(n) \approx 0.269\,n^2 + 0.399\,n + 0.25,$$

tracks `n <= 6` but misses `n = 7` (predicting `16`, not `17`) and `n = 8`
(predicting `21`, not `20`); a cubic fails the same way; no small-integer
recurrence

$$a(n) = p\,a(n-1) + q\,a(n-2) + s$$

fits exactly; and a floor form

$$\left\lfloor \frac{n^2 + c}{d} \right\rfloor + \delta$$

matches fewer than seven of the ten terms for every small `c` and `d`. We found no
closed form over the proved range.

The frontier sits at `n = 10`. The obstacle is the piece count, which jumps from
`4655` at `n = 10` to `17073` at `n = 11`; the model for `n = 11` exhausted memory
within the per-term budget before settling a value. Kagey's conjectured `a(11) =
37` and `a(12) = 43` lie just past where our search reaches, so they stay open
here. Reaching `a(11)` likely needs a more compact encoding of the placement
constraints, or a decomposition that avoids holding all `17073` pieces at once.

Two larger questions remain. First, whether any `a(n)` admits a closed form: ten
irregular terms argue against it but cannot rule out a formula that only surfaces
later. Second, whether within-window minimality equals global minimality. The
window's height and width bounds are forced; only the area cap is assumed.
Settling whether a minimal container can ever be more elongated than that cap --
by proof or by counterexample -- would close the gap.

A related sequence, A352029 (John Mason, 2022), counts the minimalist containers
rather than measuring them; it is a different quantity, noted here only for
context.

## Further reading

This work was inspired by the OEIS and the community of contributors who maintain
it.

- Kagey, P. (2019). "A327094: Smallest polyomino containing all free n-ominoes." The On-Line Encyclopedia of Integer Sequences. https://oeis.org/A327094
- Mason, J. (2022). "A352029: Number of minimalist polyominoes that can contain all n-ominoes." The On-Line Encyclopedia of Integer Sequences. https://oeis.org/A352029
- Redelmeier, D. H. (1981). "Counting Polyominoes: Yet Another Attack." Discrete Mathematics 36, 191-203.
- Sloane, N. J. A. "A000105: Number of free polyominoes (or square animals) with n cells." The On-Line Encyclopedia of Integer Sequences. https://oeis.org/A000105

## License

[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) -- see `LICENSE`. This work is freely available; a citation or acknowledgment is appreciated but not required.
