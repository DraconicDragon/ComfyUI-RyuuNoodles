import re

# todo: second textbox that updates on input_text change to work with token counter maybe?


class CleanStringAdvanced:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": ("Text input to be cleaned."),
                    },
                ),
                "strip": (
                    ["off", "left", "right", "both"],
                    {
                        "default": "both",
                        "tooltip": ("Control which side(s) of whitespace to strip from the input string."),
                    },
                ),
                "trailing_commas": (
                    ["off", "remove", "add", "add + space"],
                    {
                        "default": "remove",
                        "tooltip": (
                            "Remove or add a comma at the end of the input string.\n"
                            "Will not add a comma if one already exists, but will add a space if 'add + space' is chosen and a comma exists but no space."
                        ),
                    },
                ),
                "newlines": (
                    ["off", "remove empty", "collapse lines"],
                    {
                        "default": "off",
                        "tooltip": (
                            "Control how newlines are handled\n"
                            "off = keep all lines\n"
                            "remove empty = drop blank lines\n"
                            "collapse lines = join all lines into one"
                        ),
                    },
                ),
                "collapse": (
                    ["off", "spaces", "spaces + commas"],
                    {
                        "default": "spaces + commas",
                        "tooltip": (
                            "Collapse multiple consecutive spaces into one, or collapse both spaces and commas into a single occurrence depending on the selected option.\n"
                            "Example: 'apple,  banana,  apple,  orange.' → 'apple, banana, orange.'\n"
                        ),
                    },
                ),
                "remove_duplicate_tags": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": (
                            "Remove duplicate tags/words separated by commas, handling spaces around commas and ensuring only unique entries remain.\n"
                            "Example: 'apple, banana, apple, orange' → 'apple, banana, orange'\n"
                        ),
                    },
                ),
                "case": (
                    [
                        "off",
                        "lowercase",
                        "uppercase",
                        "capitalize",
                        "titlecase",
                        "camelcase",
                        "pascalcase",
                        "snakecase",
                        "kebabcase",
                    ],
                    {
                        "default": "off",
                        "tooltip": (
                            "Change the case of the string. Examples with input 'apple, banana, orange.':\n"
                            "off = no change ('apple, banana, orange.')\n"
                            "lowercase = all lowercase ('apple, banana, orange.')\n"
                            "uppercase = ALL UPPERCASE ('APPLE, BANANA, ORANGE.')\n"
                            "capitalize = First letter uppercase, rest lowercase ('Apple, banana, orange.')\n"
                            "titlecase = Every Word Capitalized ('Apple, Banana, Orange.')\n"
                            "camelcase = likeThisExample ('appleBananaOrange.')\n"
                            "pascalcase = LikeThisExample ('AppleBananaOrange.')\n"
                            "snakecase = like_this_example ('apple_banana_orange.')\n"
                        )
                    }
                )
            }
        }

    CATEGORY = "RyuuNoodles 🐲/Text"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "clean_text"
    EXPERIMENTAL = True

    DESCRIPTION = (
        "Cleans up and formats the given text with a set of optional filters:\n"
        "- Strip whitespace (off/left/right/both) from the input string\n"
        "- Remove or add trailing comma from the input string\n"
        "- Collapse multiple spaces in the input string\n"
        "- Convert to lowercase\n"
        "- Control newline handling (off/remove empty/collapse lines)\n"
        "\n"
        "Useful for normalizing input strings for consistent processing."
    )

    def _collapse_spaces_comma(self, collapse_commas: bool, text: str) -> str:
        # Collapse multiple spaces into one (ignoring newlines)
        if not collapse_commas:
            cleaned = re.sub(r"[ ]{2,}", " ", text)
        elif collapse_commas:
            # 1) Collapse multiple spaces/tabs (but NOT newlines) into a single space
            cleaned = re.sub(r"[ \t]{2,}", " ", text)

            # 2) Normalize comma spacing within lines
            #    Remove spaces/tabs around commas, then ensure one space after each comma
            cleaned = re.sub(r"[ \t]*,[ \t]*", ", ", cleaned)

            # 3) Collapse repeated comma+space sequences into a single ", "
            cleaned = re.sub(r"(,\s*){2,}", ", ", cleaned)

            # Optional: tidy up trailing spaces on each line (without affecting actual line breaks)
            cleaned = re.sub(r"[ \t]+(\r?\n)", r"\1", cleaned)

        return cleaned

    def _apply_case(self, text: str, case: str) -> str:
        if case == "off":
            return text
        elif case == "lowercase":
            return text.lower()
        elif case == "uppercase":
            return text.upper()
        elif case == "capitalize":
            return text.capitalize()
        elif case == "titlecase":
            return text.title()
        elif case == "camelcase":
            words = re.split(r"[\s,_-]+", text)
            if not words:
                return text
            first = words[0].lower()
            rest = [w.capitalize() for w in words[1:]]
            return first + "".join(rest)
        elif case == "pascalcase":
            words = re.split(r"[\s,_-]+", text)
            return "".join(w.capitalize() for w in words)
        elif case == "snakecase":
            words = re.split(r"[\s,_-]+", text)
            return "_".join(w.lower() for w in words if w)
        elif case == "kebabcase":
            words = re.split(r"[\s,_-]+", text)
            return "-".join(w.lower() for w in words if w)
        else:
            return text

    def clean_text(
        self,
        input_text,
        case,
        strip,
        trailing_commas,
        newlines,
        collapse,
        remove_duplicate_tags,
    ):
        # Split into lines for newline handling
        lines = input_text.splitlines()

        # Filter or collapse lines based on newlines setting
        if newlines == "remove empty":
            # Drop blank lines
            processed_lines = [line for line in lines if line.strip()]
        else:
            processed_lines = lines.copy()

        # Join lines if collapsing
        if newlines == "collapse lines":
            cleaned = " ".join(processed_lines)
        else:
            cleaned = "\n".join(processed_lines)

        if collapse == "spaces" or collapse == "spaces + commas":
            if collapse == "spaces + commas":
                cleaned = self._collapse_spaces_comma(True, cleaned)
            else:
                cleaned = self._collapse_spaces_comma(False, cleaned)

        # Strip leading/trailing whitespace
        if strip in ("left", "both"):
            cleaned = cleaned.lstrip()
        if strip in ("right", "both"):
            cleaned = cleaned.rstrip()

        # Remove unnecessary trailing comma (and space after it)
        if trailing_commas == "remove":
            cleaned = re.sub(r"(?:[ \t]*,[ \t]*)+$", "", cleaned)
        elif trailing_commas == "add":
            if cleaned and not re.search(r",[ \t]*$", cleaned):
                cleaned += ","
        elif trailing_commas == "add + space":
            if cleaned.endswith(","):
                if not cleaned.endswith(", "):
                    cleaned += " "
            elif not re.search(r",[ \t]*$", cleaned):
                cleaned += ", "

        # Remove duplicate comma-separated tags/words
        if remove_duplicate_tags is True:
            tags = [tag.strip() for tag in cleaned.split(",")]
            seen = set()
            unique_tags = []
            for tag in tags:
                if tag and tag not in seen:
                    seen.add(tag)
                    unique_tags.append(tag)
            cleaned = ", ".join(unique_tags)

        # Apply case transformation last
        cleaned = self._apply_case(cleaned, case)

        return (cleaned,)
