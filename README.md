# 🖥️ Mini SQL Compiler

> **Design and Implementation of a Mini SQL Compiler using Lexical Analysis and Recursive Descent Parsing**

A complete Mini SQL Compiler built with Python that performs Lexical Analysis, Syntax Analysis, Parse Tree Generation, and Intermediate Code Generation — with a premium Streamlit web interface.

## 📚 Syllabus Coverage

| Unit | Topics Covered |
|------|---------------|
| **Unit 1** | Lexical Analysis, Token Specification, Regular Expressions, Finite Automata, Lex |
| **Unit 2** | CFG, Recursive Descent Parsing, Predictive Parsing, FIRST/FOLLOW Sets, LALR Table, YACC |
| **Unit 3** | Syntax Trees, Postfix Notation, Three Address Code, Quadruples, Triples |
| **Unit 4** | Symbol Table |

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the compiler
streamlit run app.py
```

## 🛠️ Tech Stack

- **Python 3.x** — Main language
- **PLY (Python Lex-Yacc)** — Lexer + Parser
- **Streamlit** — Web UI
- **re module** — Regular expressions (built-in)

## 📁 Project Structure

```
mini-sql-compiler/
├── lexer.py              ← PLY Lexer (Unit 1)
├── parser.py             ← PLY Parser with CFG (Unit 2)
├── syntax_tree.py        ← Parse tree builder (Unit 3)
├── symbol_table.py       ← Symbol table manager (Unit 1+4)
├── grammar_analysis.py   ← FIRST/FOLLOW sets (Unit 2)
├── intermediate.py       ← Postfix, TAC, Quadruples (Unit 3)
├── compiler.py           ← Main pipeline
├── errors.py             ← Error handling
├── utils.py              ← Formatter, highlighter, export
├── app.py                ← Streamlit UI
└── requirements.txt      ← Dependencies
```

## ✨ Features

1. 📋 Lexical Analysis with regex patterns
2. 🎨 Syntax-highlighted query display
3. 📊 Symbol Table with identifier tracking
4. 📈 Token statistics chart
5. ✅ Syntax validation with detailed errors
6. 📜 CFG rules trace
7. 🎯 FIRST & FOLLOW sets
8. 🧮 LALR Parsing table
9. 🌳 Visual Parse Tree
10. 📐 Postfix notation conversion
11. 📝 Three Address Code generation
12. 📊 Quadruples & Triples
13. ⚡ Compile speed control
14. 🕒 Query history
15. 📥 Export compilation report

## 📝 Supported SQL Queries

```sql
SELECT name FROM students
SELECT name, age, grade FROM students
SELECT name FROM students WHERE age > 18
SELECT name FROM employees WHERE department = 'CS'
SELECT * FROM courses
SELECT name FROM students WHERE age > 18 AND grade = 'A'
INSERT INTO students VALUES (1, 'Rahul', 20)
```

## 👨‍🎓 Project Info

- **Subject**: Compiler Design (M.Sc. 2nd Semester)
- **Tools**: PLY, Streamlit, Python
