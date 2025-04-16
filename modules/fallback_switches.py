from ..modules.utils.any_type import AnyType
from ..modules.fallback_switch_base import FallbackSwitchBase

class AnySwitchFallback(FallbackSwitchBase):
    """RyuuNoodles Any Switch Fallback Node.

    This node has a boolean option and two inputs that can be any type.
    If the boolean is True, it returns input_1.
    If the boolean is False, it returns input_2_opt.
    If input_2_opt is not provided, it falls back to input_1 and a message will be printed to console.
    """

    TYPE = AnyType("*")
    INPUT_NAME_1 = "input_1"
    INPUT_NAME_2 = "input_2_opt"


class ImageSwitchFallback(FallbackSwitchBase):
    """RyuuNoodles Image Switch Fallback Node.

    This node has a boolean option and two image inputs.
    If the boolean is True, it returns image_1.
    If the boolean is False, it returns image_2_opt.
    If image_2_opt is not provided, it falls back to image_1 and a message will be printed to console.
    """

    TYPE = "IMAGE"
    INPUT_NAME_1 = "image_1"
    INPUT_NAME_2 = "image_2_opt"


class LatentSwitchFallback(FallbackSwitchBase):
    """RyuuNoodles Latent Switch Fallback Node.

    This node has a boolean option and two latent inputs.
    If the boolean is True, it returns latent_1.
    If the boolean is False, it returns latent_2_opt.
    If latent_2_opt is not provided, it falls back to latent_1 and a message will be printed to console.
    """

    TYPE = "LATENT"
    INPUT_NAME_1 = "latent_1"
    INPUT_NAME_2 = "latent_2_opt"


# class CustomSwitchFallback(FallbackSwitchBase):
#     """A Custom Switch node"""
#     TYPE = AnyType("*")
#     INPUT_NAME_1 = "custom_input_1"
#     INPUT_NAME_2 = "custom_input_2_opt"