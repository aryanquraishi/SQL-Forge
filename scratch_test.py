import sqlglot

queries = [
    "SELECT name, age FROM students WHERE age > ",
    "SELECT * FROM",
    "SELECT name age, FROM students",
    "UPDATE students SET name = 'John' WHERE",
]

for q in queries:
    print(f"--- Testing: {q} ---")
    try:
        sqlglot.parse(q, error_level=sqlglot.ErrorLevel.RAISE)
    except sqlglot.errors.ParseError as e:
        print("Exception:", str(e))
        if hasattr(e, 'errors'):
            print("Errors array:", e.errors)
