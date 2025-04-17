from ..modules.fallback_switch_base import FallbackSwitchBase
from ..modules.utils.any_type import AnyType


class FallbackSwitchAny(FallbackSwitchBase):
    TYPE = AnyType("*")
    RETURN_TYPES = (TYPE,)
    INPUT_NAME_1 = "on_true_fb"
    INPUT_NAME_2 = "on_false"


class FallbackSwitchImage(FallbackSwitchBase):
    TYPE = "IMAGE"
    RETURN_TYPES = (TYPE,)
    INPUT_NAME_1 = "on_true_fb"
    INPUT_NAME_2 = "on_false"


class FallbackSwitchLatent(FallbackSwitchBase):
    TYPE = "LATENT"
    RETURN_TYPES = (TYPE,)
    INPUT_NAME_1 = "on_true_fb"
    INPUT_NAME_2 = "on_false"


# class CustomSwitchFallback(FallbackSwitchBase):
#     """A Custom Switch node"""
#     TYPE = AnyType("*")
#     INPUT_NAME_1 = "custom_input_1"
#     INPUT_NAME_2 = "custom_input_2_opt"
