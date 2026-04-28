"""
errors.py — Custom Error Classes for Mini SQL Compiler
Handles lexer errors, syntax errors, and semantic hints with detailed messages.
Supports multi-error detection (panic mode error recovery).
"""


class CompilerError:
    """Base class for all compiler errors."""
    
    def __init__(self, error_type, message, position=None, line=None, hint=None, token_value=None):
        self.error_type = error_type      # 'LEXER', 'SYNTAX', 'SEMANTIC'
        self.message = message
        self.position = position
        self.line = line or 1
        self.hint = hint
        self.token_value = token_value
    
    def to_dict(self):
        return {
            'type': self.error_type,
            'message': self.message,
            'position': self.position,
            'line': self.line,
            'hint': self.hint,
            'token_value': self.token_value
        }
    
    def __str__(self):
        parts = [f"❌ {self.error_type} Error: {self.message}"]
        if self.token_value:
            parts.append(f"   At token: '{self.token_value}'")
        if self.position is not None:
            parts.append(f"   Position: {self.position}")
        if self.line:
            parts.append(f"   Line: {self.line}")
        if self.hint:
            parts.append(f"   💡 Hint: {self.hint}")
        return "\n".join(parts)


class LexerError(CompilerError):
    """Error during lexical analysis — invalid/illegal characters."""
    
    def __init__(self, char, position, line=1):
        super().__init__(
            error_type="LEXER",
            message=f"Illegal character '{char}'",
            position=position,
            line=line,
            hint=f"Character '{char}' is not recognized. Check for typos or unsupported symbols.",
            token_value=char
        )


class SyntaxError(CompilerError):
    """Error during syntax analysis — grammar rule violation."""
    
    def __init__(self, message, token_value=None, position=None, line=1, expected=None, hint=None):
        if expected and not hint:
            hint = f"Expected: {expected}"
        super().__init__(
            error_type="SYNTAX",
            message=message,
            position=position,
            line=line,
            hint=hint,
            token_value=token_value
        )
        self.expected = expected


class SemanticWarning(CompilerError):
    """Warning during semantic check — not a hard error but suspicious."""
    
    def __init__(self, message, position=None, hint=None):
        super().__init__(
            error_type="SEMANTIC",
            message=message,
            position=position,
            hint=hint
        )
    
    def __str__(self):
        parts = [f"⚠️ Warning: {self.message}"]
        if self.hint:
            parts.append(f"   💡 Hint: {self.hint}")
        return "\n".join(parts)


class ErrorCollector:
    """
    Collects multiple errors during compilation.
    Supports panic mode error recovery — continues parsing after errors.
    """
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def add_error(self, error):
        """Add a CompilerError to the collection."""
        if isinstance(error, SemanticWarning):
            self.warnings.append(error)
        else:
            self.errors.append(error)
    
    def add_lexer_error(self, char, position, line=1):
        """Convenience method for lexer errors."""
        self.errors.append(LexerError(char, position, line))
    
    def add_syntax_error(self, message, token_value=None, position=None, line=1, expected=None, hint=None):
        """Convenience method for syntax errors."""
        self.errors.append(SyntaxError(message, token_value, position, line, expected, hint))
    
    def add_warning(self, message, position=None, hint=None):
        """Convenience method for semantic warnings."""
        self.warnings.append(SemanticWarning(message, position, hint))
    
    def has_errors(self):
        """Check if any errors were collected."""
        return len(self.errors) > 0
    
    def has_warnings(self):
        """Check if any warnings were collected."""
        return len(self.warnings) > 0
    
    def get_error_count(self):
        """Get total error count."""
        return len(self.errors)
    
    def get_warning_count(self):
        """Get total warning count."""
        return len(self.warnings)
    
    def get_summary(self):
        """Get a summary string of all errors and warnings."""
        parts = []
        for i, error in enumerate(self.errors, 1):
            parts.append(f"Error {i}: {error}")
        for i, warning in enumerate(self.warnings, 1):
            parts.append(f"Warning {i}: {warning}")
        
        total = f"\nFound {len(self.errors)} error(s)"
        if self.warnings:
            total += f", {len(self.warnings)} warning(s)"
        parts.append(total)
        
        return "\n\n".join(parts)
    
    def clear(self):
        """Clear all collected errors and warnings."""
        self.errors.clear()
        self.warnings.clear()
    
    def to_list(self):
        """Return all errors and warnings as list of dicts."""
        result = []
        for e in self.errors:
            result.append(e.to_dict())
        for w in self.warnings:
            d = w.to_dict()
            d['type'] = 'WARNING'
            result.append(d)
        return result


# ============================================================
#  Smart Error Hints — Context-aware suggestions
# ============================================================

SYNTAX_HINTS = {
    'SELECT_NO_COLUMNS': {
        'message': "Missing column names after SELECT",
        'expected': "Column names (e.g., name, age) or * for all columns",
        'hint': "SELECT ke baad column names likhein — Example: SELECT name, age FROM students"
    },
    'MISSING_FROM': {
        'message': "Missing FROM keyword",
        'expected': "FROM keyword after column list",
        'hint': "Column names ke baad FROM likhna zaroori hai — Example: SELECT name FROM students"
    },
    'MISSING_TABLE': {
        'message': "Missing table name after FROM",
        'expected': "Table name (IDENTIFIER) after FROM",
        'hint': "FROM ke baad table ka naam likhein — Example: FROM students"
    },
    'MISSING_WHERE_CONDITION': {
        'message': "Missing condition after WHERE",
        'expected': "Condition expression (e.g., age > 18)",
        'hint': "WHERE ke baad condition likhein — Example: WHERE age > 18"
    },
    'INVALID_OPERATOR': {
        'message': "Invalid or missing operator in condition",
        'expected': "Comparison operator: >, <, =, >=, <=, !=",
        'hint': "Valid operators: > (greater), < (less), = (equal), >= (greater equal), <= (less equal), != (not equal)"
    },
    'MISSING_VALUE': {
        'message': "Missing value in condition",
        'expected': "Number, string, or identifier after operator",
        'hint': "Operator ke baad ek value chahiye — Example: age > 18 or name = 'Rahul'"
    },
    'TRAILING_COMMA': {
        'message': "Trailing comma in column list",
        'expected': "Column name after comma",
        'hint': "Comma ke baad ek aur column name likhein ya comma hatao"
    },
    'INSERT_SYNTAX': {
        'message': "Invalid INSERT syntax",
        'expected': "INSERT INTO table_name VALUES (value1, value2, ...)",
        'hint': "Correct format: INSERT INTO students VALUES (1, 'Rahul', 20)"
    },
    'UNEXPECTED_END': {
        'message': "Unexpected end of query",
        'expected': "Query is incomplete",
        'hint': "Query adhuri hai — check karein ki saare parts complete hain"
    },
    'GENERAL': {
        'message': "Syntax error in query",
        'expected': "Valid SQL syntax",
        'hint': "Check SQL query format — Example: SELECT column FROM table WHERE condition"
    }
}


def get_smart_hint(error_context):
    """Get a smart hint based on the error context."""
    hint_data = SYNTAX_HINTS.get(error_context, SYNTAX_HINTS['GENERAL'])
    return hint_data
