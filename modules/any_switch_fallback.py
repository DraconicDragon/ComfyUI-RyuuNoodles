class AnySwitchFallback:
    """RyuuNoodles Any Switch Fallback Node.
    This node takes a boolean input and two image inputs.
    If the boolean is True, it returns image_1.
    If the boolean is False, it returns image2.
    If image2 is not provided, it falls back to image_1.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "NotImplemented",
                    },
                ),
                "image_1": ("IMAGE",),
            },
            "optional": {
                "image_2_opt": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "do_thing"
    OUTPUT_NODE = True

    CATEGORY = "RyuuNoodles/Util"

    def do_thing(
        self,
        boolean,
        image_1,
        image_2_opt=None,
    ):
        if boolean:
            return (image_1,)
        else:
            if image_2_opt is not None:
                return (image_2_opt,)
            else:
                print("No image_2_opt provided, falling back to image_1")
                return (image_1,)
