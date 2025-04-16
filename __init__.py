from .modules.fallback_passthrough import FallbackPassthrough
from .modules.fallback_switches import *

NODE_CLASS_MAPPINGS = {
    "FallbackSwitchAny": FallbackSwitchAny,
    "FallbackSwitchImage": FallbackSwitchImage,
    "FallbackSwitchLatent": FallbackSwitchLatent,
    "FallbackPassthrough": FallbackPassthrough,
}

NODE_DISPLAY_NAME_MAPPINGS = { # maybe use 🍜 instead so colors clash less with custom scripts?
    "FallbackSwitchAny": "Switch Any Fallback 🐲",
    "FallbackSwitchImage": "Switch Image Fallback 🐲",
    "FallbackSwitchLatent": "Switch Latent Fallback 🐲",
    "FallbackPassthrough": "Passthrough 🐲",
}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
