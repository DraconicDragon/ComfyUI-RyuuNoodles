import math


class ScalingUtils:
    """
    Utility class for scaling operations shared between Scale To Multiple and latent size picker node(s).
    """

    # todo: revisit when nodespec v3
    @staticmethod
    def scale_int(val, rounding_mode, scale_factor, multiple):
        """
        Scale integer value, then round to nearest/floor/ceil multiple.

        Args:
            val: The value to scale (can be None)
            rounding_mode: "nearest", "floor", or "ceil"
            scale_factor: Factor to multiply by before rounding
            multiple: The multiple to round to

        Returns:
            Scaled and rounded integer, or None if val is None
        """
        if val is None:
            return None
        val = int(round(val * scale_factor))

        if rounding_mode == "nearest":
            return int(round(val / multiple) * multiple)
        elif rounding_mode == "floor":
            return int(math.floor(val / multiple) * multiple)
        elif rounding_mode == "ceil":
            return int(math.ceil(val / multiple) * multiple)
        else:
            return val

    @staticmethod
    def create_rounding_mode_inputs(separate_modes=False):
        """
        Create rounding mode input definitions for ComfyUI nodes.

        Args:
            separate_modes: If True, creates separate inputs for width/height

        Returns:
            Dictionary of input definitions
        """
        inputs = {}

        if separate_modes:
            inputs["rounding_mode_width"] = (
                ["nearest", "floor", "ceil"],
                {
                    "default": "nearest",
                    "tooltip": (
                        "Rounding mode for width. "
                        "'nearest' will round to the nearest multiple of 'multiple' value.\n"
                        "'floor' will round down to the nearest multiple. \n"
                        "'ceil' will round up."
                    ),
                },
            )
            inputs["rounding_mode_height"] = (
                ["nearest", "floor", "ceil"],
                {
                    "default": "nearest",
                    "tooltip": (
                        "Rounding mode for height. "
                        "'nearest' will round to the nearest multiple of 'multiple' value.\n"
                        "'floor' will round down to the nearest multiple. \n"
                        "'ceil' will round up."
                    ),
                },
            )
        else:
            inputs["rounding_mode"] = (
                ["nearest", "floor", "ceil"],
                {
                    "default": "nearest",
                    "tooltip": (
                        "Rounding mode for both width and height. "
                        "'nearest' will round to the nearest multiple of 'multiple' value.\n"
                        "'floor' will round down to the nearest multiple. \n"
                        "'ceil' will round up."
                    ),
                },
            )

        return inputs

    @staticmethod
    def create_scale_factor_inputs(separate_factors=False):
        """
        Create scale factor input definitions for ComfyUI nodes.

        Args:
            separate_factors: If True, creates separate inputs for width/height

        Returns:
            Dictionary of input definitions
        """
        inputs = {}

        if separate_factors:
            inputs["scale_factor_width"] = (
                "FLOAT",
                {
                    "default": 1.0,
                    "min": 0.01,
                    "step": 0.005,
                    "tooltip": ("How much to multiply width by before scaling to multiple."),
                },
            )
            inputs["scale_factor_height"] = (
                "FLOAT",
                {
                    "default": 1.0,
                    "min": 0.01,
                    "step": 0.005,
                    "tooltip": ("How much to multiply height by before scaling to multiple."),
                },
            )
        else:
            inputs["scale_factor"] = (
                "FLOAT",
                {
                    "default": 1.0,
                    "min": 0.01,
                    "step": 0.005,
                    "tooltip": ("How much to multiply both width and height by before scaling to multiple."),
                },
            )

        return inputs

    @staticmethod
    def extract_scaling_params(kwargs, separate_modes=False, separate_factors=False):
        """
        Extract scaling parameters from kwargs based on configuration.

        Args:
            kwargs: Dictionary of parameters
            separate_modes: Whether separate rounding modes are used
            separate_factors: Whether separate scale factors are used

        Returns:
            Tuple of (rounding_mode_width, rounding_mode_height, scale_factor_width, scale_factor_height)
        """
        # Extract rounding mode parameters
        if separate_modes:
            rounding_mode_width = kwargs["rounding_mode_width"]
            rounding_mode_height = kwargs["rounding_mode_height"]
        else:
            rounding_mode = kwargs["rounding_mode"]
            rounding_mode_width = rounding_mode_height = rounding_mode

        # Extract scale factor parameters
        if separate_factors:
            scale_factor_width = kwargs["scale_factor_width"]
            scale_factor_height = kwargs["scale_factor_height"]
        else:
            scale_factor = kwargs["scale_factor"]
            scale_factor_width = scale_factor_height = scale_factor

        return rounding_mode_width, rounding_mode_height, scale_factor_width, scale_factor_height
