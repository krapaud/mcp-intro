# Study Assistant Response

**Question:** I want to study Python decorators. What should I review first?

## Recommended topic: Python Decorators

**Why it's relevant:** Decorators are functions that wrap another function to extend or modify its behavior without changing its source code.

**Prerequisites:**
- Functions
- Scope
- First-class functions

**Key concepts:**
- Higher-order functions
- Wrapper functions
- functools.wraps
- Closures

**Common mistakes to avoid:**
- Forgetting to return the wrapper function
- Not preserving the original function's metadata with functools.wraps
- Confusing decorator arguments with the decorated function's arguments

**Practice idea:** Create a decorator that logs the name and execution time of any function it wraps.
