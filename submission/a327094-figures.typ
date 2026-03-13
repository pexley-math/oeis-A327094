#set page(
  paper: "a4",
  margin: (top: 2cm, bottom: 2cm, left: 1.5cm, right: 1.5cm),
  header: context {
    if counter(page).get().first() > 1 [
      #align(center)[#text(size: 8pt, fill: luma(120))[A327094: Smallest Polyomino Containing All Free n-ominoes]]
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
  #text(size: 16pt, weight: "bold")[A327094: Smallest Polyomino Containing All Free n-ominoes]
  #v(0.3em)
  #text(size: 10pt)[Smallest connected polyomino that contains every free n-omino]
  #v(0.2em)
  #text(size: 10pt)[SAT-Proved Optimal: a(9) = 26]
  #v(0.2em)
  #text(size: 8pt, style: "italic")[Computed by Peter Exley, March 2026]
]
#v(0.5em)
#line(length: 100%, stroke: 0.5pt)
#v(0.3em)

#block(breakable: false, width: 100%)[
  #align(center)[
    #text(size: 11pt, weight: "bold")[a(9) = 26]
    #h(0.5em)
    #text(size: 8pt, weight: "bold", fill: rgb("#27AE60"))[\[PROVED\]]
  ]
  #align(center)[
    #text(size: 8pt)[5 X 9 bounding box, contains all 1285 free 9-ominoes]
  ]
  #v(0.3em)
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
      table.cell(fill: white)[],
    )
  ]
  #v(0.5em)
]

#v(0.5em)
#line(length: 100%, stroke: 0.5pt)
