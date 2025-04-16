from .modules.fallback_passthrough import FallbackPassthrough
from .modules.fallback_switches import *

NODE_CLASS_MAPPINGS = {
    "Ryuu_FallbackSwitchAny": FallbackSwitchAny,
    "Ryuu_FallbackSwitchImage": FallbackSwitchImage,
    "Ryuu_FallbackSwitchLatent": FallbackSwitchLatent,
    "Ryuu_FallbackPassthrough": FallbackPassthrough,
}

NODE_DISPLAY_NAME_MAPPINGS = { # maybe use 🍜 instead so colors clash less with custom scripts?
    "Ryuu_FallbackSwitchAny": "Switch Any Fallback 🐲",
    "Ryuu_FallbackSwitchImage": "Switch Image Fallback 🐲",
    "Ryuu_FallbackSwitchLatent": "Switch Latent Fallback 🐲",
    "Ryuu_FallbackPassthrough": "Passthrough 🐲",
}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
