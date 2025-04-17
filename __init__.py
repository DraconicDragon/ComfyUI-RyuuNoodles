from .modules.fallback_passthrough import FallbackPassthrough
from .modules.fallback_switches import *
from .modules.number_ops import FloatPlain, FloatSlider, IntSlider
from .modules.token_count_textbox import TokenCountTextBox

from .pyserver import update_token_count

NODE_CLASS_MAPPINGS = {
    "Ryuu_FallbackSwitchAny": FallbackSwitchAny,
    "Ryuu_FallbackSwitchImage": FallbackSwitchImage,
    "Ryuu_FallbackSwitchLatent": FallbackSwitchLatent,
    "Ryuu_FallbackPassthrough": FallbackPassthrough,
    "Ryuu_FloatSlider": FloatSlider,
    "Ryuu_FloatPlain": FloatPlain,
    "Ryuu_IntSlider": IntSlider,
    "Ryuu_TokenCountTextBox": TokenCountTextBox,
}

NODE_DISPLAY_NAME_MAPPINGS = {  # maybe use 🍜 instead so colors clash less with custom scripts?
    "Ryuu_FallbackSwitchAny": "Switch Any Fallback 🐲",
    "Ryuu_FallbackSwitchImage": "Switch Image Fallback 🐲",
    "Ryuu_FallbackSwitchLatent": "Switch Latent Fallback 🐲",
    "Ryuu_FallbackPassthrough": "Passthrough 🐲",
    "Ryuu_FloatSlider": "Float Slider 🐲",
    "Ryuu_FloatPlain": "Float 🐲",
    "Ryuu_IntSlider": "Int Slider 🐲",
    "Ryuu_TokenCountTextBox": "Token Count Textbox 🐲",
}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
