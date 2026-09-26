path = "src/genai_client.py"
lines = open(path, "r", encoding="utf-8").readlines()

count = 0
for i, line in enumerate(lines):
    if "max_tokens=300," in line:
        lines[i] = line.replace("max_tokens=300,", "max_tokens=600,")
        count += 1

open(path, "w", encoding="utf-8").writelines(lines)
print(f"Replaced {count} occurrence(s) of max_tokens=300.")
