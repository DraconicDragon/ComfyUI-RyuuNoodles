from ..modules.scale_to_multiple_base import ScaleToMultipleBase


class ScaleToMultiple(ScaleToMultipleBase):
    """
    Scales image dimensions and/or integers to a specified multiple, with simplified controls.
    Simple version with unified controls for both width and height.
    """

    # Use default flags (both False) for simplified interface
    ALLOW_SEPARATE_ROUNDING_MODES = False
    ALLOW_SEPARATE_SCALE_FACTORS = False

    DESCRIPTION = (
        "Scales image dimensions and/or integers to a specified multiple, with simplified controls.\n"
        "If no image is provided, only the width and height will be scaled.\n"
        "If image and width and/or height is provided, the image will use the "
        "provided dimension for scaling instead of it's own width/height. This will work as a width/height override."
    )
