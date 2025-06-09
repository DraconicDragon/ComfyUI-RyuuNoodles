from .modules.clean_strings import CleanStringAdvanced
from .modules.color_matcher_bpfriendly import ColorMatch
from .modules.extract_lora import ExtractAndSaveLora
from .modules.fallback_passthrough import FallbackPassthrough
from .modules.fallback_switches import (
    FallbackSwitchAny,
    FallbackSwitchImage,
    FallbackSwitchLatent,
)
from .modules.primitive_number_ops import (
    FloatPlain,
    FloatPlainLarger,
    FloatSlider,
    IntSlider,
)
from .modules.tenc_weight_diff_check import TextEncoderDiffCheck
from .modules.token_count_textbox import TokenCountTextBox

# to get the routes registered
from .pyserver import update_token_count

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
    # Image nodes
    "Ryuu_ColorMatch": ColorMatch,
    # Token Counter
    "Ryuu_TokenCountTextBox": TokenCountTextBox,
    # Experimental Nodes/Utils
    "Ryuu_TextEncoderDiffCheck": TextEncoderDiffCheck,
    "Ryuu_ExtractAndSaveLora": ExtractAndSaveLora,
    # String cleaning/stripping nodes
    "Ryuu_CleanStringAdvanced": CleanStringAdvanced,
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
    "Ryuu_ColorMatch": "Color Match 🐲",
    "Ryuu_TokenCountTextBox": "Textbox 🐲",
    # Experimental Nodes/Utils
    "Ryuu_TextEncoderDiffCheck": "Check Text Encoder Diff 🐲",
    "Ryuu_ExtractAndSaveLora": "Extract and Save Lora 🐲",
        "Ryuu_CleanStringAdvanced": "Clean String Advanced 🐲",

}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
