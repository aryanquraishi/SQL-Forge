import sqlglot

queries = [
    "SELECT nam, age FRM students",
    "SELECT name, age FROM students WHERE age ==",
]

for q in queries:
    print(f"--- Testing: {q} ---")
    try:
        sqlglot.parse(q, error_level=sqlglot.ErrorLevel.RAISE)
    except sqlglot.errors.ParseError as e:
        print("Exception:", str(e))
        if hasattr(e, 'errors'):
            print("Errors array:", e.errors)
