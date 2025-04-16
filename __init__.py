from .modules.fallback_switches import *

NODE_CLASS_MAPPINGS = {
    "FallbackSwitchAny": FallbackSwitchAny,
    "FallbackSwitchImage": FallbackSwitchImage,
    "FallbackSwitchLatent": FallbackSwitchLatent,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FallbackSwitchAny": "Switch Any Fallback 🐲",
    "FallbackSwitchImage": "Switch Image Fallback 🐲",
    "FallbackSwitchLatent": "Switch Latent Fallback 🐲",
}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
