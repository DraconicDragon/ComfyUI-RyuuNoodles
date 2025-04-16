from .modules.any_switch_fallback import *


NODE_CLASS_MAPPINGS = {
    "AnySwitchFallback": AnySwitchFallback,
    "ImageSwitchFallback": ImageSwitchFallback,
    "LatentSwitchFallback": LatentSwitchFallback,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AnySwitchFallback": "Switch Any Fallback",
    "ImageSwitchFallback": "Switch Image Fallback",
    "SwitchFallback": "Switch Latent Fallback",
}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
