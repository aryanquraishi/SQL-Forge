"""
ai_assistant.py — AI Chatbot for Mini SQL Compiler
Uses Groq API (LLaMA model) to provide intelligent assistance.
The AI knows about:
  - Compiler Design concepts (all 5 units)
  - This project's architecture and features
  - SQL query writing help
  - Can explain compilation steps
"""

import os
from groq import Groq


# ============================================================
#  System Prompt — Project Knowledge + Compiler Expertise
# ============================================================

SYSTEM_PROMPT = """You are an intelligent AI assistant for a Mini SQL Compiler project built for an M.Sc. Compiler Design course. You are embedded inside the compiler's Streamlit web interface.

## CORE CAPABILITY & ROLE:
- You are an unrestricted, highly intelligent AI Agent capable of discussing any topic or acting on any request.
- You are not limited to just answering compiler questions. You can act as a general-purpose smart assistant.
- You have deep context about this Mini SQL Compiler project, but you should also readily answer non-compiler questions if asked.

## PROJECT DETAILS:
This Mini SQL Compiler is built with Python using PLY (Python Lex-Yacc) library and has these phases:

### Phase 1 — Lexical Analysis (Unit 1):
- Uses PLY's lex module with Regular Expressions to tokenize SQL queries
- Token types: KEYWORD, IDENTIFIER, NUMBER, STRING, OPERATOR, SYMBOL
- Internally uses DFA (Deterministic Finite Automaton) for pattern matching
- Regex patterns: [a-zA-Z_][a-zA-Z0-9_]* for identifiers, \\d+(\\.\\d+)? for numbers
- Case-insensitive keyword matching via reserved word dictionary lookup

### Phase 2 — Syntax Analysis (Unit 2):
- Uses PLY's yacc module (LALR(1) parser internally)
- Context-Free Grammar (CFG) rules define valid SQL syntax
- Grammar rules:
  query → select_stmt | insert_stmt
  select_stmt → SELECT columns FROM table_name [WHERE condition]
  columns → * | column_list
  column_list → IDENTIFIER | IDENTIFIER , column_list
  condition → expression [AND|OR condition]
  expression → IDENTIFIER operator value
  operator → > | < | = | >= | <= | !=
  value → NUMBER | STRING | IDENTIFIER
  insert_stmt → INSERT INTO IDENTIFIER VALUES (value_list)
- FIRST and FOLLOW sets are computed for predictive parsing
- Detailed error messages with position and hints

### Phase 3 — Syntax Tree (Unit 3):
- Parse tree generated from valid AST
- TreeNode class with name, children, value attributes
- Visual tree display with ├── └── │ connectors

### Phase 4 — Intermediate Code (Unit 3):
- Postfix Notation: infix to postfix conversion of WHERE conditions
- Three Address Code (TAC): t1 = age > 18, t2 = SELECT ... FROM ...
- Quadruples: (operator, arg1, arg2, result) format
- Triples: (index, operator, arg1, arg2) format

### Phase 5 — Symbol Table (Unit 4):
- Tracks all identifiers: name, category (COLUMN/TABLE/VALUE), position, frequency, context

### Supported SQL:
- SELECT name FROM students
- SELECT name, age FROM students
- SELECT * FROM courses
- SELECT name FROM students WHERE age > 18
- SELECT name FROM students WHERE age > 18 AND grade = 'A'
- INSERT INTO students VALUES (1, 'Rahul', 20)

### Tech Stack:
- Python 3.x, PLY (lex + yacc), Streamlit, re module

## SYLLABUS MAPPING:
- Unit 1: Lexical Analysis, Token Specification, Regular Expressions, Finite Automata, Lex
- Unit 2: CFG, Top-Down Parsing, Recursive Descent, Predictive Parsing, Bottom-Up, LALR, YACC
- Unit 3: Syntax Trees, Postfix Notation, Three Address Code, Quadruples, Triples
- Unit 4: Symbol Table, Storage Organization
- Unit 5: Code Optimization, Basic Blocks (partially covered)

## REFERENCES:
1. Aho, Lam, Sethi, Ullman — "Compilers: Principles, Techniques, and Tools" (Dragon Book)
2. Mogensen — "Introduction to Compiler Design" (3rd ed., Springer, 2024)
3. PLY Documentation — ply.readthedocs.io
4. Beazley, D. — PLY (Python Lex-Yacc) Documentation

## YOUR ROLE & PERSONALITY:
- You are a highly intelligent, unrestricted AI Agent. You are not limited to just answering compiler questions; you can discuss any topic, assist with any task, and act as a general-purpose smart assistant.
- You have deep context about this Mini SQL Compiler project (details below), and you should use this knowledge when the user asks related questions.
- However, if the user asks about something else, or gives a general command (e.g., "make this bigger", "write a python script", "who is the president"), you MUST obey and fulfill their request intelligently without saying "Invalid input" or restricting yourself.
- Be highly capable, creative, and professional. You act as an expert command runner and assistant.

## RESPONSE STYLE:
- Respond in Professional English, but you can understand and reply in Hindi/Hinglish if the user prefers it or talks to you in Hindi.
- Be intelligent, technical, and precise. 
- Do NOT restrict yourself. If the user asks for a big SQL query, give them a massive one. Obey the user's prompt exactly.
- Keep responses concise and formatting clean. Use code blocks for code.
- No unnecessary greetings, filler words, or repetition. Skip introductions like "Sure, I can help."
"""


# ============================================================
#  AI Chat Function
# ============================================================

def get_ai_response(messages, api_key, model="llama-3.3-70b-versatile"):
    """
    Get AI response from Groq API.
    
    Args:
        messages: List of message dicts [{role, content}]
        api_key: Groq API key
        model: Model to use
    
    Returns:
        str: AI response text, or error message
    """
    if not api_key or api_key.strip() == "":
        return "⚠️ Please enter your Groq API key in the sidebar to use the AI Assistant."
    
    try:
        client = Groq(api_key=api_key.strip())
        
        # Prepend system prompt
        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        
        chat_completion = client.chat.completions.create(
            messages=full_messages,
            model=model,
            temperature=0.7,
            max_tokens=1024,
            top_p=0.9,
        )
        
        return chat_completion.choices[0].message.content
    
    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
            return "❌ Invalid API key. Please check your Groq API key and try again."
        elif "rate_limit" in error_msg.lower():
            return "⏳ Rate limit reached. Please wait a moment and try again."
        else:
            return f"❌ Error: {error_msg}"


def get_query_suggestion(query_description, api_key):
    """
    Get AI to suggest a SQL query based on description.
    
    Args:
        query_description: Natural language description
        api_key: Groq API key
    
    Returns:
        str: Suggested SQL query
    """
    messages = [{
        "role": "user",
        "content": f"Write a SQL query for: {query_description}\n\nIMPORTANT: Only use SQL syntax that this Mini SQL Compiler supports (SELECT, FROM, WHERE, INSERT INTO). Return ONLY the SQL query, no explanation."
    }]
    
    return get_ai_response(messages, api_key)


# Quick prompts for the UI
QUICK_PROMPTS = [
    "Explain how lexical analysis works in this compiler",
    "What is a Context-Free Grammar? Explain with this project's example",
    "Explain FIRST and FOLLOW sets with an example",
    "What is the difference between Top-Down and Bottom-Up parsing?",
    "Explain Three Address Code with an example",
    "What are Quadruples and Triples in intermediate code?",
    "Write a SQL query to select all students with grade A",
    "What is a Symbol Table and why is it important?",
    "Explain how the Parse Tree is constructed",
    "What is Postfix notation? Convert age > 18 AND name = 'Rahul' to postfix",
]
