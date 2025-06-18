from ..modules.scale_to_multiple_base import ScaleToMultipleBase


class ScaleToMultipleAdvanced(ScaleToMultipleBase):
    """
    Scales image dimensions and/or integers to a specified multiple, with options for rounding mode and pre-scaling.
    Advanced version with separate controls for width and height.
    """

    # Enable advanced features
    ALLOW_SEPARATE_ROUNDING_MODES = True
    ALLOW_SEPARATE_SCALE_FACTORS = True

    DESCRIPTION = (
        "Scales image dimensions and/or integers to a specified multiple, with options for rounding mode and pre-scaling.\n"
        "If no image is provided, only the width and height will be scaled.\n"
        "If image and width and/or height is provided, the image will use the "
        "provided dimension for scaling instead of it's own width/height. This will work as a width/height override."
    )
