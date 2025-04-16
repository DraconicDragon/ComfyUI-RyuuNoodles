from .modules.any_switch_fallback import *


NODE_CLASS_MAPPINGS = {
    "AnySwitchFallback": AnySwitchFallback,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AnySwitchFallback": "Any Switch Fallback",
}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
