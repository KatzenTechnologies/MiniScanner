import string

class Localization:
    def __init__(self, data):
        self.language_name = data.get("language_name", "Unknown")
        self.translations = data.get("translation", {})

    def translate(self, key: str, **kwargs) -> str:
        template_str = self.translations.get(key, f"[{key}]")
        try:
            template = string.Template(template_str)
            return template.safe_substitute(**kwargs)
        except Exception as e:
            return f"[Error: {e}]"
