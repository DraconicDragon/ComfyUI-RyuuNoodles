from ..modules.utils.any_type import AnyType
from ..modules.utils.ryuu_print import ryuu_print


class FallbackSwitchBase:
    """Base class for fallback switch nodes."""

    TYPE = AnyType("*")  # Override in subclasses if needed
    INPUT_NAME_1 = "input_1"
    INPUT_NAME_2 = "input_2_opt"
    TOOLTIP_BOOL = (
        "True will output {input_1}, False will try to output {input_2_opt}. "
        "If {input_2_opt} is not provided (e.g. the connected node is muted or bypassed), it will fall back to {input_1}. "
        "A message will be printed to console if this happens."
    )
    TOOLTIP_INPUT_1 = (
        "The input to output if boolean is True. Will be used as fallback if {input_2_opt} is not provided."
    )
    TOOLTIP_INPUT_2 = (
        "The input to output if boolean is False. If not provided (e.g. the connected node is muted or bypassed), "
        "{input_1} will be used as fallback and a message will be printed to console if this happens. This input is optional."
    )

    DESCRIPTION = (
        "This node allows for 2 inputs where the second input is chosen if it's provided as well as if the boolean switch is set to false, "
        "and otherwise the first input is used as fallback. "
        "Use the boolean switch to choose preference between the two inputs. "
        'If you want the same node without the boolean input, use "Passthrough 🐲"'
    )

    CATEGORY = "RyuuNoodles/Util"
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
                        "tooltip": cls.TOOLTIP_INPUT_1.format(
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
                        "tooltip": cls.TOOLTIP_INPUT_2.format(
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
