"""Stylesheet for the final-evaluation deck.

Kept in its own module so the deck builder stays readable and the CSS can be
tweaked without touching the slide markup.
"""

STYLE = """
@page { size: 338.7mm 190.5mm; margin: 0; }

*, *::before, *::after { box-sizing: border-box; }

html, body {
  margin: 0;
  padding: 0;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

body {
  font-family: "Public Sans", -apple-system, "Segoe UI", sans-serif;
  color: #2b211b;
  background: #f8f5f1;
}

.slide {
  width: 338.7mm;
  height: 190.5mm;
  padding: 13mm 15mm 11mm;
  position: relative;
  overflow: hidden;
  page-break-after: always;
  break-after: page;
  display: flex;
  flex-direction: column;
  background: #f8f5f1;
}

.slide:last-child { page-break-after: auto; break-after: auto; }

.slide--dark {
  background: #1b1612;
  color: #efe9e2;
}

/* ------------------------------------------------------------------ chrome */

.rail {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8mm;
  padding-bottom: 2.5mm;
  border-bottom: 0.6pt solid #c9bfb4;
  font-family: "IBM Plex Mono", monospace;
  font-size: 7.4pt;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #8a7f76;
  flex: none;
}

.slide--dark .rail { border-color: #3a2f28; color: #9a8d82; }

.rail b { color: #2b211b; font-weight: 500; }
.slide--dark .rail b { color: #efe9e2; }

.body { flex: 1 1 auto; min-height: 0; padding-top: 7mm; display: flex; flex-direction: column; }

/* Content that should fill the slide body without overflowing it. */
.fill { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; justify-content: space-between; }

/* --------------------------------------------------------------- typography */

h1 {
  font-family: "Newsreader", Georgia, serif;
  font-size: 40pt;
  line-height: 1.02;
  font-weight: 600;
  letter-spacing: -0.028em;
  margin: 0;
  max-width: 15ch;
}

h2 {
  font-family: "Newsreader", Georgia, serif;
  font-size: 25pt;
  line-height: 1.08;
  font-weight: 600;
  letter-spacing: -0.022em;
  margin: 0 0 3mm;
  max-width: 26ch;
}

h3 {
  font-family: "Public Sans", sans-serif;
  font-size: 9.6pt;
  font-weight: 600;
  letter-spacing: 0.01em;
  margin: 0 0 1.6mm;
}

p { margin: 0 0 3mm; font-size: 10.4pt; line-height: 1.5; max-width: 62ch; }

.lede { font-size: 12.4pt; line-height: 1.45; color: #4a3d34; max-width: 54ch; }
.slide--dark .lede { color: #c4b8ad; }

.mono {
  font-family: "IBM Plex Mono", monospace;
  font-variant-numeric: tabular-nums;
}

.accent { color: #a63a1e; }
.slide--dark .accent { color: #e08a5f; }

/* ------------------------------------------------------------------- stats */

.stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  border-top: 1.2pt solid #2b211b;
  border-bottom: 0.6pt solid #c9bfb4;
  margin-top: auto;
}

.slide--dark .stats { border-top-color: #efe9e2; border-bottom-color: #3a2f28; }

.stat {
  padding: 4mm 4mm 4mm 0;
  border-left: 0.6pt solid #ddd4ca;
  padding-left: 4mm;
  min-width: 0;
}

.stat:first-child { border-left: 0; padding-left: 0; }
.slide--dark .stat { border-left-color: #3a2f28; }

.stat .k {
  font-family: "IBM Plex Mono", monospace;
  font-size: 7pt;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: #8a7f76;
  display: block;
}

.stat .v {
  font-family: "Newsreader", Georgia, serif;
  font-size: 27pt;
  font-weight: 600;
  letter-spacing: -0.03em;
  line-height: 1;
  margin-top: 2mm;
  font-variant-numeric: tabular-nums;
}

.stat .v small {
  font-family: "Public Sans", sans-serif;
  font-size: 9pt;
  font-weight: 500;
  letter-spacing: 0;
  color: #8a7f76;
}

.stat .n { font-size: 8pt; color: #8a7f76; margin-top: 1.6mm; line-height: 1.4; }

/* ------------------------------------------------------------------ layout */

.split { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 10mm; }
.split--wide { grid-template-columns: minmax(0, 1.35fr) minmax(0, 1fr); }
.split--narrow { grid-template-columns: minmax(0, 1fr) minmax(0, 1.5fr); }

/* ------------------------------------------------------------------ tables */

table { width: 100%; border-collapse: collapse; font-size: 8.6pt; font-variant-numeric: tabular-nums; }

thead th {
  text-align: left;
  padding: 1.8mm 2mm;
  border-bottom: 1pt solid #2b211b;
  font-family: "IBM Plex Mono", monospace;
  font-size: 6.8pt;
  font-weight: 500;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color: #8a7f76;
  white-space: nowrap;
}

tbody td { padding: 1.7mm 2mm; border-bottom: 0.5pt solid #e2dad1; }
tbody tr:last-child td { border-bottom: 1pt solid #2b211b; font-weight: 600; }
td.num, th.num { text-align: right; }

.slide--dark thead th { border-bottom-color: #efe9e2; color: #9a8d82; }
.slide--dark tbody td { border-bottom-color: #3a2f28; }
.slide--dark tbody tr:last-child td { border-bottom-color: #efe9e2; }

/* ------------------------------------------------------------------ images */

.shot {
  border: 0.6pt solid #c9bfb4;
  display: block;
  width: 100%;
  height: auto;
}

.shot-wrap { position: relative; }

.caption {
  font-family: "IBM Plex Mono", monospace;
  font-size: 6.8pt;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: #8a7f76;
  margin-top: 1.8mm;
}

/* ------------------------------------------------------------------- lists */

.findings { list-style: none; margin: 0; padding: 0; }

.findings li {
  display: grid;
  grid-template-columns: 7mm minmax(0, 1fr);
  gap: 3mm;
  padding: 2.6mm 0;
  border-bottom: 0.5pt solid #e2dad1;
}

.slide--dark .findings li { border-bottom-color: #3a2f28; }

.findings .idx {
  font-family: "IBM Plex Mono", monospace;
  font-size: 7.4pt;
  color: #a63a1e;
  padding-top: 0.6mm;
}

.slide--dark .findings .idx { color: #e08a5f; }

.findings p { margin: 0; font-size: 9.4pt; line-height: 1.45; max-width: none; }

/* ------------------------------------------------------------------ footer */

.foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6mm;
  padding-top: 2.5mm;
  border-top: 0.6pt solid #c9bfb4;
  font-family: "IBM Plex Mono", monospace;
  font-size: 6.8pt;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #8a7f76;
  flex: none;
}

.slide--dark .foot { border-color: #3a2f28; color: #9a8d82; }

/* --------------------------------------------------------------- title slide */

.title-slide { justify-content: space-between; }

.title-slide .mark { color: #a63a1e; flex: none; }

.title-slide h1 { font-size: 33pt; max-width: 22ch; }

.title-slide .lede { font-size: 11.4pt; max-width: 62ch; }

.title-slide .kicker {
  font-family: "IBM Plex Mono", monospace;
  font-size: 8pt;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #a63a1e;
  margin-bottom: 5mm;
}

.title-slide .byline {
  font-size: 10.4pt;
  line-height: 1.6;
  color: #4a3d34;
  margin-top: 5mm;
  padding-bottom: 4mm;
}

.title-slide .byline b { color: #2b211b; font-weight: 600; }

/* ------------------------------------------------------------------- bars */

.bar-row { display: grid; grid-template-columns: 34mm minmax(0, 1fr) 12mm; align-items: center; gap: 3mm; padding: 1.5mm 0; }
.bar-row .lbl { font-size: 8.6pt; color: #4a3d34; }
.bar-row .track { height: 3.4mm; background: #e8e0d7; position: relative; }
.bar-row .fill { position: absolute; inset: 0 auto 0 0; background: #a63a1e; }
.bar-row .val { font-family: "IBM Plex Mono", monospace; font-size: 8.4pt; text-align: right; font-variant-numeric: tabular-nums; }

.slide--dark .bar-row .lbl { color: #c4b8ad; }
.slide--dark .bar-row .track { background: #3a2f28; }
.slide--dark .bar-row .fill { background: #e08a5f; }
"""
