from ..modules.shared.any_type import AnyType

any_type = AnyType("*")


class IsMultipleOf:
    """
    Checks if a given integer is a multiple of a specified value.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "number_a": (
                    any_type,
                    {
                        "default": None,
                        "min": 1,
                        "tooltip": (
                            "The number to check if it is a multiple of the 'multiple' value.\n" "Required input. "
                        ),
                    },
                ),
                "multiple": ("INT", {"default": 64, "min": 1}),
                "error_if_b_none": (
                    "BOOLEAN",
                    {"default": False, "tooltip": ("If True, will raise an error if number_b is None.")},
                ),
                "false_instead_none": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": (
                            "If True, will output False instead of None if number_b is None.\n"
                            "This does not bypass the error_if_b_none option."
                        ),
                    },
                ),
            },
            "optional": {
                "number_b": (
                    any_type,
                    {
                        "default": None,
                        "min": 1,
                        "tooltip": ("Optional second number to check if it is also a multiple of the same value."),
                    },
                ),
            },
        }

    RETURN_TYPES = ("BOOLEAN", "BOOLEAN")
    RETURN_NAMES = ("is_a_multiple_of", "is_b_multiple_of")

    FUNCTION = "check_multiple"

    EXPERIMENTAL = True

    DESCRIPTION = (
        "Simple node to check if an input number and/or the optional second number "
        "is a multiple of the specified 'multiple' value. "
        "Outputs Booleans. If number_b is not given, will output None."
    )

    CATEGORY = "RyuuNoodles 🐲/Numbers"

    def check_multiple(self, number_a, multiple, error_if_b_none, false_instead_none, number_b=None):
        if number_b is None and error_if_b_none:
            raise ValueError(
                "number_b is None and errored because 'error_if_b_none' is set to True. "
                "Please provide a valid number_b or set 'error_if_b_none' to False.\n"
                f"Values: number_a: {number_a}, number_b: {number_b}, multiple: {multiple}"
            )

        if number_a is None or multiple is None:
            raise ValueError(
                "Either 'number_a' or 'multiple' is None. "
                "Both 'number_a' and 'multiple' must be provided and cannot be None.\n"
                f"Values: number_a: {number_a}, number_b: {number_b}, multiple: {multiple}"
            )

        # tolerance for float comparisons due to potential precision issues
        tolerance = 1e-8
        is_a_multiple = abs(number_a % multiple) < tolerance

        # If number_b is provided, check if both are multiples
        if number_b is not None:
            is_b_multiple = abs(number_b % multiple) < tolerance
            return (is_a_multiple, is_b_multiple)

        # If number_b is None, return False if false_instead_none is True, else None
        return (is_a_multiple, False if false_instead_none else None)
