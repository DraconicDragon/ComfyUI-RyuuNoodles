class TokenCountTextBox:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {"default": "", "multiline": True}),
            }
        }

    CATEGORY = "RyuuNoodles/Util"

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "dooooooooodooooo"

    def dooooooooodooooo(self, input_text):

        return {"ui": {"text": input_text}, "result": (input_text,)}

