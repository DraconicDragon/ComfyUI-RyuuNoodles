class CleanStringAdvanced:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": (
                    "STRING",
                    {"default": "", "multiline": True, "tooltip": "Text input to be cleaned."},
                ),
            },
            "optional": {
                "strip": (
                    "COMBO",
                    {
                        "default": "both",
                        "choices": ["off", "left", "right", "both"],
                        "tooltip": "Control which side(s) of whitespace to strip from each line.",
                    },
                ),
                "trailing_comma": (
                    "COMBO",
                    {
                        "default": "remove",
                        "choices": ["off", "remove", "add", "add + space"],
                        "tooltip": "Remove or add a comma at the end of each line.",
                    },
                ),
                "collapse_spaces": (
                    "BOOLEAN",
                    {"default": True, "tooltip": "Replace multiple spaces in a line with a single space."},
                ),
                "to_lowercase": (
                    "BOOLEAN",
                    {"default": False, "tooltip": "Convert all characters in the string to lowercase."},
                ),
                "collapse_lines": (
                    "BOOLEAN",
                    {"default": False, "tooltip": "Join all lines into a single line with spaces between them."},
                ),
                "preserve_empty_lines": (
                    "BOOLEAN",
                    {"default": True, "tooltip": "Keep empty lines in the final output."},
                ),
            },
        }

    CATEGORY = "RyuuNoodles/Util"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "clean_text"

    DESCRIPTION = (
        "Cleans up and formats the given text with a set of optional filters:\n"
        "- Strip whitespace (off/left/right/both)\n"
        "- Remove or add trailing comma\n"
        "- Collapse multiple spaces\n"
        "- Convert to lowercase\n"
        "- Collapse lines into one\n"
        "- Optionally preserve empty lines\n\n"
        "Useful for normalizing input strings for consistent processing.\n"
        "Token counters will reflect the cleaned result."
    )

    def clean_text(
        self,
        input_text,
        strip,
        trailing_comma,
        collapse_spaces,
        to_lowercase,
        collapse_lines,
        preserve_empty_lines,
    ):
        lines = input_text.splitlines()
        cleaned_lines = []

        for line in lines:
            if strip in ("left", "both"):
                line = line.lstrip()
            if strip in ("right", "both"):
                line = line.rstrip()

            if trailing_comma == "remove" and line.endswith(","):
                line = line[:-1]
            elif trailing_comma == "add" and not line.endswith(",") and line:
                line = line + ","

            if collapse_spaces:
                line = " ".join(line.split())

            if to_lowercase:
                line = line.lower()

            if preserve_empty_lines or line:
                cleaned_lines.append(line)

        if collapse_lines:
            cleaned = " ".join(cleaned_lines)
        else:
            cleaned = "\n".join(cleaned_lines)

        return (cleaned,)
