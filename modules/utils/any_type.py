class AnyType(str):
    """A special type that can be connected to any other types. Credit to pythongosssss, and receyuki/comfyui-prompt-reader-node"""

    def __ne__(self, __value: object) -> bool:
        return False
