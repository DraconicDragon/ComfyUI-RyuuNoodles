from .modules.clean_strings_advanced import CleanStringAdvanced
from .modules.color_matcher_bpfriendly import ColorMatch
from .modules.extract_lora import ExtractAndSaveLora
from .modules.fallback_passthrough import FallbackPassthrough
from .modules.fallback_switches import (
    FallbackSwitchAny,
    FallbackSwitchImage,
    FallbackSwitchLatent,
)
from .modules.is_multiple_of import IsMultipleOf
from .modules.primitive_number_ops import (
    FloatPlain,
    FloatPlainLarger,
    FloatSlider,
    IntSlider,
)
from .modules.scale_to_multiple import ScaleToMultiple
from .modules.scale_to_multiple_advanced import ScaleToMultipleAdvanced
from .modules.tenc_weight_diff_check import TextEncoderDiffCheck
from .modules.token_count_textbox import TokenCountTextBox
from .modules.z_test_node import RyuuTestNode

# to get the routes registered
from .pyserver import update_token_count  # noqa: F401

NODE_CLASS_MAPPINGS = {
    # Switches and Passthrough nodes
    "Ryuu_FallbackPassthrough": FallbackPassthrough,
    "Ryuu_FallbackSwitchAny": FallbackSwitchAny,
    "Ryuu_FallbackSwitchImage": FallbackSwitchImage,
    "Ryuu_FallbackSwitchLatent": FallbackSwitchLatent,
    # Number operation nodes
    "Ryuu_FloatPlain": FloatPlain,
    "Ryuu_FloatPlainLarger": FloatPlainLarger,
    "Ryuu_FloatSlider": FloatSlider,
    "Ryuu_IntSlider": IntSlider,
    "Ryuu_IsMultipleOf": IsMultipleOf,
    # Image nodes
    "Ryuu_ColorMatch": ColorMatch,
    # Token Counter
    "Ryuu_TokenCountTextBox": TokenCountTextBox,
    # Experimental Nodes/Utils
    "Ryuu_ScaleToMultipleAdvanced": ScaleToMultipleAdvanced,
    "Ryuu_ScaleToMultiple": ScaleToMultiple,
    "Ryuu_TextEncoderDiffCheck": TextEncoderDiffCheck,
    "Ryuu_ExtractAndSaveLora": ExtractAndSaveLora,
    # String cleaning/stripping nodes
    "Ryuu_CleanStringAdvanced": CleanStringAdvanced,
    "Ryuu_TestNode": RyuuTestNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {  # maybe use 🍜 instead so colors clash less with custom scripts?
    "Ryuu_FallbackSwitchAny": "Switch Any Fallback 🐲",
    "Ryuu_FallbackSwitchImage": "Switch Image Fallback 🐲",
    "Ryuu_FallbackSwitchLatent": "Switch Latent Fallback 🐲",
    "Ryuu_FallbackPassthrough": "Passthrough 🐲",
    "Ryuu_FloatSlider": "Float Slider 🐲",
    "Ryuu_FloatPlain": "Float 🐲",
    "Ryuu_FloatPlainLarger": "Float L 🐲",
    "Ryuu_IntSlider": "Int Slider 🐲",
    "Ryuu_IsMultipleOf": "test Is Multiple Of x Check 🐲",
    "Ryuu_ColorMatch": "Color Match 🐲",
    "Ryuu_TokenCountTextBox": "Textbox 🐲",
    # Experimental Nodes/Utils
    "Ryuu_ScaleToMultipleAdvanced": "Scale To Multiple Adv. 🐲",
    "Ryuu_ScaleToMultiple": "Scale To Multiple 🐲",
    "Ryuu_TextEncoderDiffCheck": "Check Text Encoder Diff 🐲",
    "Ryuu_ExtractAndSaveLora": "Extract and Save Lora 🐲",
    "Ryuu_CleanStringAdvanced": "Clean String Adv. 🐲",
    "Ryuu_TestNode": "🚧 Ryuu Test Node 🐲",
}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
