from ..modules.utils.any_type import AnyType
from ..modules.utils.ryuu_print import ryuu_print

any_type = AnyType("*")


class FallbackPassthrough:
    """RyuuNoodles Fallback Passthrough Node.
    This node has two inputs. If input_2_opt is provided, it will be used.
    Otherwise input_1 will be used as fallback.
    This node is similar to the Switch nodes except that there is no boolean input."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_1": (
                    any_type,
                    {
                        "tooltip": "Will be used as fallback if input_2_opt is not provided.",
                    },
                ),
            },
            "optional": {
                "input_2_opt": (
                    any_type,
                    {
                        "tooltip": "Will be used if provided, otherwise input_1 will be used as fallback",
                    },
                )
            },
        }

    RETURN_TYPES = (any_type,)
    FUNCTION = "do_thing"
    OUTPUT_NODE = True

    DESCRIPTION = "This node allows for 2 inputs where input_2_opt is chosen if it's provided and otherwise input_1 is used as fallback."

    CATEGORY = "RyuuNoodles/Switches"

    def do_thing(self, input_1, input_2_opt=None):
        if input_2_opt is not None:
            return (input_2_opt,)
        else:
            ryuu_print("No input_2_opt provided, falling back to input_1")
            return (input_1,)
