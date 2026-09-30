# Where to find material for each section of the PDF report

| Report section | Source in this repo |
|---|---|
| 1. Cover page | Your name, reg. no., course, faculty, date |
| 2. Introduction | README.md "Overview" |
| 3. Problem statement | statement.md |
| 4–5. Functional / Non-functional requirements | docs/DESIGN.md §1–2 |
| 6. System architecture | docs/DESIGN.md §3 |
| 7. Design diagrams | docs/DESIGN.md §4–8 (export from https://mermaid.live as PNG) |
| 8. Design decisions & rationale | docs/DESIGN.md §9 |
| 9. Implementation details | one paragraph per module in `smart_calculator/` |
| 10. Screenshots / results | run the app and capture the terminal |
| 11. Testing approach | `python -m unittest discover -s tests -v` output, README "Testing" |
| 12. Challenges faced | e.g. operator precedence & right-associative `^`, implicit multiplication, safe evaluation, floating-point display, solver verification |
| 13. Learnings | parsing, modular design, error handling, testing, Git |
| 14. Future enhancements | graph plotting, GUI (Tkinter/web), symbolic algebra, currency conversion, matrix operations |
| 15. References | Python docs, Mermaid docs, course material |
