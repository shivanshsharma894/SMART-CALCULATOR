# Design Document – Smart Calculator

(Diagrams are written in Mermaid, which GitHub renders automatically. Export them as images for the PDF report, e.g. via https://mermaid.live.)

## 1. Functional requirements
| ID | Requirement |
|---|---|
| FR1 | Evaluate arithmetic expressions with precedence, parentheses, functions, constants |
| FR2 | Store variables (`x = 5`) and reuse the last result (`ans`); switch degree/radian mode |
| FR3 | Convert between units in 8 categories |
| FR4 | Solve linear/quadratic equations from text and n×n linear systems |
| FR5 | Compute descriptive statistics for a list of numbers |
| FR6 | Keep history: create, read/search, delete, clear; persist between sessions |
| FR7 | Interactive REPL and one-shot command-line mode |

**Input/Output:** input is one text line (expression or `:command`); output is a formatted result or an `Error: …` message.

## 2. Non-functional requirements
| Type | Requirement |
|---|---|
| Security | No `eval`/`exec`; whitelisted grammar; limits on length (500), exponent (10 000), factorial (1 000) |
| Reliability | Custom exceptions; REPL never crashes; history file written atomically; corrupt history file is ignored |
| Usability | Clear error messages with position info; `:help`; implicit multiplication (`2x`) |
| Performance | Any supported expression evaluates in well under 10 ms |
| Maintainability | 11 small modules, one responsibility each; type hints and docstrings; 38 unit tests; CI |
| Logging | Rotating log file records every calculation and failure |
| Resource efficiency | Standard library only; history capped at 500 entries |

## 3. System architecture
```mermaid
flowchart LR
    U[User] --> CLI[cli.py<br/>REPL & command router]
    CLI --> ENG[engine.py<br/>Calculator]
    CLI --> UN[units.py]
    CLI --> SOL[solver.py]
    CLI --> ST[stats.py]
    ENG --> PAR[parser.py<br/>tokenizer + parser + evaluator]
    ENG --> FUN[functions.py]
    SOL --> PAR
    ENG --> HIS[history.py]
    HIS --> FILE[(history.json)]
    CLI --> FMT[formatting.py]
    ENG --> LOG[logger.py]
    LOG --> LF[(calculator.log)]
```

## 4. Workflow diagram
```mermaid
flowchart TD
    A([Start]) --> B[/Enter a line/]
    B --> C{Starts with ':'?}
    C -- yes --> D[Route to command handler<br/>convert / solve / stats / history ...]
    C -- no --> E[Tokenize]
    E --> F[Parse to AST]
    F --> G[Evaluate safely]
    G --> H[Format result]
    H --> I[Save to history + log]
    D --> J[Display output]
    I --> J
    E -. error .-> K[Show Error message]
    F -. error .-> K
    G -. error .-> K
    D -. error .-> K
    K --> B
    J --> B
```

## 5. Use case diagram
```mermaid
flowchart LR
    User((User))
    subgraph Smart Calculator
        UC1[Evaluate expression]
        UC2[Store variable / use ans]
        UC3[Convert units]
        UC4[Solve equation / system]
        UC5[Compute statistics]
        UC6[View / search history]
        UC7[Delete / clear history]
        UC8[Change angle mode]
    end
    User --> UC1 & UC2 & UC3 & UC4 & UC5 & UC6 & UC7 & UC8
```

## 6. Sequence diagram (evaluating `2x+1` after `x = 5`)
```mermaid
sequenceDiagram
    actor User
    participant CLI as CalculatorCLI
    participant Calc as Calculator
    participant P as Parser/Evaluator
    participant H as History
    User->>CLI: "2x+1"
    CLI->>Calc: calculate("2x+1")
    Calc->>P: evaluate_expression(text, variables, functions)
    P->>P: tokenize → parse → evaluate
    P-->>Calc: 11
    Calc->>H: add("2x+1", "11")
    H-->>Calc: entry saved (JSON)
    Calc-->>CLI: 11
    CLI-->>User: "11"
```

## 7. Class / component diagram
```mermaid
classDiagram
    class CalculatorCLI { +handle(line) str }
    class Calculator { +angle_mode +variables +last_result +calculate(expr) +set_angle_mode(mode) }
    class History { +add() +all() +get() +search() +delete() +clear() }
    class HistoryEntry { +id +expression +result +timestamp }
    class Parser { +parse() +expr() +term() +unary() +power() +primary() }
    class CalculatorError
    CalculatorError <|-- ParseError
    CalculatorError <|-- EvaluationError
    CalculatorError <|-- UnitError
    CalculatorError <|-- SolverError
    CalculatorError <|-- StatsError
    CalculatorError <|-- HistoryError
    CalculatorCLI --> Calculator
    Calculator --> History
    History "1" o-- "*" HistoryEntry
    Calculator ..> Parser : uses
```

## 8. Storage design (ER)
History is stored as a JSON list.
```mermaid
erDiagram
    HISTORY ||--o{ HISTORY_ENTRY : contains
    HISTORY_ENTRY {
        int id PK
        string expression
        string result
        string timestamp
    }
```

## 9. Design decisions & rationale
- **Recursive-descent parser instead of `eval`** – safe by construction, gives good error messages, and demonstrates compiler concepts (tokenizer, grammar, AST).
- **Equation solver reuses the evaluator** – f(x)=lhs−rhs is sampled at three points to recover a,b,c, then verified at three more points; avoids writing a separate algebra parser.
- **Gaussian elimination with partial pivoting** – numerically stable, detects singular systems.
- **JSON history with atomic writes** – human readable, no database needed, safe against crashes.
- **Standard library only** – zero install friction for evaluators.
- **CLI `handle()` returns strings** – makes the interface fully unit-testable.
