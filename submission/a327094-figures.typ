#set page(
  paper: "a4",
  margin: (top: 2cm, bottom: 2cm, left: 1.5cm, right: 1.5cm),
  header: context {
    if counter(page).get().first() > 1 [
      #align(center)[#text(size: 8pt, fill: luma(120))[A327094: Smallest Polyomino Containing All Free $n$-ominoes]]
    ]
  },
  footer: context {
    let current = counter(page).get().first()
    let total = counter(page).final().first()
    align(center)[#text(size: 8pt, fill: luma(120))[Page #current of #total]]
  },
)
#set text(font: "New Computer Modern", size: 9pt)

#align(center)[
  #text(size: 16pt, weight: "bold")[A327094: Smallest Polyomino Containing All Free $n$-ominoes]
  #v(0.3em)
  #text(size: 10pt)[$a(n)$ = minimum cells in a polyomino containing all free $n$-ominoes as subshapes]
  #v(0.2em)
  #text(size: 10pt)[$a(9) = 26$, $a(10) = 31$]
  #v(0.2em)
  #text(size: 8pt, style: "italic")[Computed by Peter Exley, March 2026]
]
#v(0.5em)
#line(length: 100%, stroke: 0.5pt)
#v(0.3em)
#block(breakable: false, width: 100%)[
#align(center)[
  #text(size: 11pt, weight: "bold")[$a(9) = 26$]#text(size: 8pt, fill: rgb("#27AE60"), weight: "bold")[ \[PROVED\]]
  #h(0.5em)
  #text(size: 8pt)[5 \u{00D7} 9 bounding box, 26 cells, contains all 1285 free 9-ominoes]
]
#v(0.2em)
#align(center)[
#table(
  columns: (7mm,) * 9,
  rows: (7mm,) * 5,
  inset: 0pt,
  stroke: 0.5pt + white,
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
)
]
]
#v(0.5em)
#block(breakable: false, width: 100%)[
#align(center)[
  #text(size: 11pt, weight: "bold")[$a(10) = 31$]#text(size: 8pt, fill: rgb("#27AE60"), weight: "bold")[ \[PROVED\]]
  #h(0.5em)
  #text(size: 8pt)[5 \u{00D7} 10 bounding box, 31 cells, contains all 4655 free 10-ominoes]
]
#v(0.2em)
#align(center)[
#table(
  columns: (7mm,) * 10,
  rows: (7mm,) * 5,
  inset: 0pt,
  stroke: 0.5pt + white,
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
)
]
]
#v(0.5em)
#line(length: 100%, stroke: 0.5pt)