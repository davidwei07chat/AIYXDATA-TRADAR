import sys

with open("aiyxdata_tradar/report/html_v2.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    try:
        # Check if the line is part of a docstring or f-string and contains unescaped braces
        if "{" in line and "}" in line:
            # simple heurustic, test f-string evaluation
            eval(f"f'''{line}'''")
    except NameError as e:
        if "width" in str(e):
            print(f"Error on line {i+1}: {line.strip()}")
            sys.exit(0)
    except SyntaxError:
        pass
    except Exception:
        pass

print("Not found line by line, let's look for block errors")
content = "".join(lines)
import ast
try:
    ast.parse(content)
except SyntaxError as e:
    print(f"Syntax error at {e.lineno}: {e.text}")
