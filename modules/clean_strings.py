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
                "strip_left": (
                    "BOOLEAN",
                    {"default": True, "tooltip": "Remove whitespace at the beginning of each line."},
                ),
                "strip_right": (
                    "BOOLEAN",
                    {"default": True, "tooltip": "Remove whitespace at the end of each line."},
                ),
                "remove_trailing_comma": (
                    "BOOLEAN",
                    {"default": True, "tooltip": "Remove a comma if it appears at the end of a line."},
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
        "- Strip left/right whitespace\n"
        "- Remove trailing comma\n"
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
        strip_left=True,
        strip_right=True,
        remove_trailing_comma=True,
        collapse_spaces=True,
        to_lowercase=False,
        collapse_lines=False,
        preserve_empty_lines=True,
    ):
        lines = input_text.splitlines()

        cleaned_lines = []
        for line in lines:
            original_line = line
            if strip_left:
                line = line.lstrip()
            if strip_right:
                line = line.rstrip()
            if remove_trailing_comma and line.endswith(","):
                line = line[:-1]
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
