from ..common import AnyType, ryuu_print

any_type = AnyType("*")


class AnySwitchFallback:
    """RyuuNoodles Any Switch Fallback Node.
    This node takes a boolean input and two image inputs.
    If the boolean is True, it returns input_1.
    If the boolean is False, it returns image2.
    If image2 is not provided, it falls back to input_1 and a message will be printed to console.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "True will output input_1, False will try to output input_2_opt. "
                        + "If input_2_opt is not provided (if for example the connected node is muted or bypassed), it will fall back to input_1. "
                        + "A message will be printed to console if this happens.",
                    },
                ),
                "input_1": (
                    any_type,
                    {
                        "tooltip": "The image to output if boolean is True. Will be used as fallback if input_2_opt is not provided",
                    },
                ),
            },
            "optional": {
                "input_2_opt": (
                    any_type,
                    {
                        "tooltip": "The image to output if boolean is False. If not provided, input_1 will be used as fallback."
                    },
                ),
            },
        }

    RETURN_TYPES = (any_type,)
    FUNCTION = "do_thing"
    OUTPUT_NODE = True

    CATEGORY = "RyuuNoodles/Util"

    def do_thing(self, boolean, input_1, input_2_opt=None):
        if boolean:
            return (input_1,)
        else:
            if input_2_opt is not None:
                return (input_2_opt,)
            else:
                ryuu_print("No input_2_opt provided, falling back to input_1")
                return (input_1,)
