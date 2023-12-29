import re
import json


class TextParserMixin:
    def parse_json(self, generated_text: str) -> dict:
        return json.loads(generated_text)
    
    def parse_code_snippet(self, generated_text: str, lang='python') -> str:
        pattern = rf'```{lang}\n(.*?)\n```'
        matches = re.findall(pattern, generated_text, re.DOTALL)
        return "\n".join(matches)
