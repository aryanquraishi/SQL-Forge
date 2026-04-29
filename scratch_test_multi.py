import sqlglot

queries = [
    "SELECT *\nFROM students\nWHERE",
    "SELECT\nname,\nFROM students",
]

for q in queries:
    print(f"--- Testing: {q} ---")
    try:
        sqlglot.parse(q, error_level=sqlglot.ErrorLevel.RAISE)
    except sqlglot.errors.ParseError as e:
        print("Exception:", str(e))
        if hasattr(e, 'errors'):
            print("Errors array:", e.errors)
