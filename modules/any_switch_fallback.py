from ..common import AnyType, ryuu_print

any_type = AnyType("*")


class AnySwitchFallback:
    """RyuuNoodles Any Switch Fallback Node.
    This node takes a boolean input and two image inputs.
    If the boolean is True, it returns image_1.
    If the boolean is False, it returns image2.
    If image2 is not provided, it falls back to image_1 and a message will be printed to console.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "True will output image_1, False will try to output image_2_opt. "
                        + "If image_2_opt is not provided (if for example the connected node is muted or bypassed), it will fall back to image_1. "
                        + "A message will be printed to console if this happens.",
                    },
                ),
                "image_1": (
                    any_type,
                    {
                        "tooltip": "The image to output if boolean is True. Will be used as fallback if image_2_opt is not provided",
                    },
                ),
            },
            "optional": {
                "image_2_opt": (
                    any_type,
                    {
                        "tooltip": "The image to output if boolean is False. If not provided, image_1 will be used as fallback."
                    },
                ),
            },
        }

    RETURN_TYPES = (any_type,)
    FUNCTION = "do_thing"
    OUTPUT_NODE = True

    CATEGORY = "RyuuNoodles/Util"

    def do_thing(self, boolean, image_1, image_2_opt=None):
        if boolean:
            return (image_1,)
        else:
            if image_2_opt is not None:
                return (image_2_opt,)
            else:
                ryuu_print("No image_2_opt provided, falling back to image_1")
                return (image_1,)
