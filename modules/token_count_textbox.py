class TokenCountTextBox:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {"default": "", "multiline": True}),
            }
        }

    CATEGORY = "RyuuNoodles/Text"

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "dooooooooodooooo"

    DESCRIPTION = (
        "A simple textbox. It is meant to show a token counter ontop of the textbox widget by default "
        "and serve as an example for setting up token counters on custom nodes.\n"
        "Please see the 'RyuuNoodles 🐲' settings page to configure the token counter."
    )

    def dooooooooodooooo(self, input_text):

        return {"ui": {"text": input_text}, "result": (input_text,)}
