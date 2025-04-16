from ..common import AnyType, ryuu_print


class BaseSwitchFallback:
    """Base class for fallback switch nodes."""

    TYPE = AnyType("*")  # Override in subclasses if needed
    INPUT_NAME_1 = "input_1"
    INPUT_NAME_2 = "input_2_opt"
    TOOLTIP_BOOL = (
        "True will output {input_1}, False will try to output {input_2_opt}. "
        "If {input_2_opt} is not provided (e.g. the connected node is muted or bypassed), it will fall back to {input_1}. "
        "A message will be printed to console if this happens."
    )
    TOOLTIP_1 = "The input to output if boolean is True. Will be used as fallback if {input_2_opt} is not provided."
    TOOLTIP_2 = (
        "The input to output if boolean is False. If not provided (e.g. the connected node is muted or bypassed), "
        "{input_1} will be used as fallback and a message will be printed to console if this happens. This input is optional."
    )

    CATEGORY = "RyuuNoodles/Util/Switches"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": cls.TOOLTIP_BOOL.format(
                            input_1=cls.INPUT_NAME_1,
                            input_2_opt=cls.INPUT_NAME_2,
                        ),
                    },
                ),
                cls.INPUT_NAME_1: (
                    cls.TYPE,
                    {
                        "tooltip": cls.TOOLTIP_1.format(
                            input_1=cls.INPUT_NAME_1,
                            input_2_opt=cls.INPUT_NAME_2,
                        ),
                    },
                ),
            },
            "optional": {
                cls.INPUT_NAME_2: (
                    cls.TYPE,
                    {
                        "tooltip": cls.TOOLTIP_2.format(
                            input_1=cls.INPUT_NAME_1,
                            input_2_opt=cls.INPUT_NAME_2,
                        ),
                    },
                )
            },
        }

    RETURN_TYPES = (TYPE,)
    FUNCTION = "do_thing"

    def do_thing(self, boolean, **kwargs):
        input_1 = kwargs.get(self.INPUT_NAME_1)
        input_2_opt = kwargs.get(self.INPUT_NAME_2)
        if boolean:
            return (input_1,)
        elif input_2_opt is not None:
            return (input_2_opt,)
        else:
            ryuu_print(f"No {self.INPUT_NAME_2} provided, falling back to {self.INPUT_NAME_1}")
            return (input_1,)


class AnySwitchFallback(BaseSwitchFallback):
    """RyuuNoodles Any Switch Fallback Node.

    This node has a boolean option and two inputs that can be any type.
    If the boolean is True, it returns input_1.
    If the boolean is False, it returns input_2_opt.
    If input_2_opt is not provided, it falls back to input_1 and a message will be printed to console.
    """

    TYPE = AnyType("*")
    INPUT_NAME_1 = "input_1"
    INPUT_NAME_2 = "input_2_opt"


class ImageSwitchFallback(BaseSwitchFallback):
    """RyuuNoodles Image Switch Fallback Node.

    This node has a boolean option and two image inputs.
    If the boolean is True, it returns image_1.
    If the boolean is False, it returns image_2_opt.
    If image_2_opt is not provided, it falls back to image_1 and a message will be printed to console.
    """

    TYPE = "IMAGE"
    INPUT_NAME_1 = "image_1"
    INPUT_NAME_2 = "image_2_opt"


class LatentSwitchFallback(BaseSwitchFallback):
    """RyuuNoodles Latent Switch Fallback Node.

    This node has a boolean option and two latent inputs.
    If the boolean is True, it returns latent_1.
    If the boolean is False, it returns latent_2_opt.
    If latent_2_opt is not provided, it falls back to latent_1 and a message will be printed to console.
    """

    TYPE = "LATENT"
    INPUT_NAME_1 = "latent_1"
    INPUT_NAME_2 = "latent_2_opt"
