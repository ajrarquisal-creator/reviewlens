path = "src/genai_client.py"
content = open(path, "r", encoding="utf-8").read()

old_tokens = """                temperature=0.2,
                max_tokens=300,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content
            result = json.loads(raw)

            required_fields = ["sentiment", "confidence", "keywords", "summary"]"""

new_tokens = """                temperature=0.2,
                max_tokens=500,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content
            result = json.loads(raw)

            required_fields = ["sentiment", "confidence", "keywords", "summary"]"""

content = content.replace(old_tokens, new_tokens)
print("max_tokens increased:", "max_tokens=500" in content)

open(path, "w", encoding="utf-8").write(content)
