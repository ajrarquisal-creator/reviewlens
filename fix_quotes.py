path = "app.py"
content = open(path, "r", encoding="utf-8").read()

broken1 = "return f\"background-color: {colors.get(val, \x27\x27\x27\x27)}\""
fixed1 = "return f\"background-color: {colors.get(val, \x27\x27)}\""

count = content.count(broken1)
content = content.replace(broken1, fixed1)

open(path, "w", encoding="utf-8").write(content)
print(f"Fixed {count} broken line(s).")
