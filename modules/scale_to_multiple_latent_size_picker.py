# Code from Empty Latent Size picker (misc.py at https://github.com/cubiq/ComfyUI_essentials | MIT License)

import torch

import comfy.model_management
from nodes import MAX_RESOLUTION

from .shared.scaling_utils import ScalingUtils


class ScaleToMultipleLatentSizePicker:
    """
    Latent size picker with scaling to multiple capabilities.
    Combines predefined 1MP resolutions with the ability to scale dimensions
    to specific multiples using rounding modes and scale factors.
    """

    def __init__(self):
        self.device = comfy.model_management.intermediate_device()

    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "required": {
                "resolution": (
                    [
                        "704x1472 (11:23)",
                        "640x1536 (5:12)",
                        "640x1600 (2:5)",
                        "576x1664 (9:26)",
                        "576x1728 (1:3)",
                        "704x1408 (1:2)",
                        "704x1344 (11:21)",
                        "768x1344 (4:7)",
                        "768x1280 (3:5)",
                        "768x1216 (12:19)",
                        "832x1216 (13:19)",
                        "832x1152 (13:18)",
                        "896x1152 (7:9)",
                        "960x1088 (15:17)",
                        "960x1024 (15:16)",
                        "1024x1024 (1:1)",
                        "1024x960 (16:15)",
                        "1088x960 (17:15)",
                        "1088x896 (17:14)",
                        "1152x896 (9:7)",
                        "1152x832 (18:13)",
                        "1216x832 (19:13)",
                        "1216x768 (19:12)",
                        "1280x768 (5:3)",
                        "1280x704 (20:11)",
                        "1344x768 (7:4)",
                        "1344x704 (21:11)",
                        "1408x704 (2:1)",
                        "1536x640 (12:5)",
                        "1600x640 (5:2)",
                        "1664x576 (26:9)",
                        "1728x576 (3:1)",
                    ],
                    {
                        "default": "1024x1024 (1:1)",
                        "tooltip": ("Select a predefined resolution or use overrides."),
                    },
                ),
                "multiple": (
                    "INT",
                    {
                        "default": 64,
                        "min": 0,
                        "step": 8,
                        "tooltip": ("Multiple to scale to.\n Setting to 1 effectively disables this."),
                    },
                ),
            }
        }

        # Add scaling inputs after multiple
        inputs["required"].update(ScalingUtils.create_rounding_mode_inputs(separate_modes=False))
        inputs["required"].update(ScalingUtils.create_scale_factor_inputs(separate_factors=False))

        # Add remaining inputs
        inputs["required"].update(
            {
                "batch_size": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": 4096,
                        "tooltip": ("Number of latent samples to generate."),
                    },
                ),
                "width_override": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": MAX_RESOLUTION,
                        "step": 8,
                        "tooltip": ("Override width. Set to 0 to use resolution width."),
                    },
                ),
                "height_override": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": MAX_RESOLUTION,
                        "step": 8,
                        "tooltip": ("Override height. Set to 0 to use resolution height."),
                    },
                ),
            }
        )

        return inputs

    RETURN_TYPES = ("LATENT", "INT", "INT")
    RETURN_NAMES = ("latent", "width", "height")
    FUNCTION = "execute"
    CATEGORY = "RyuuNoodles/Utils"

    DESCRIPTION = (
        "Create latent samples with SDXL resolutions and scaling to multiple capabilities.\n"
        "Combines predefined 1MP resolutions with the ability to scale dimensions "
        "to specific multiples using rounding modes and scale factors."
    )

    def execute(self, resolution, batch_size, width_override=0, height_override=0, multiple=64, **kwargs):
        multiple = 1 if multiple < 1 else multiple  # prevent zero or negative multiples

        # Extract base resolution
        width_str, height_str = resolution.split(" ")[0].split("x")

        width = int(width_str)
        height = int(height_str)

        # Extract scaling parameters
        rounding_mode_width, rounding_mode_height, scale_factor_width, scale_factor_height = (
            ScalingUtils.extract_scaling_params(kwargs, separate_modes=False, separate_factors=False)
        )

        # Apply scaling
        scaled_width = ScalingUtils.scale_int(width, rounding_mode_width, scale_factor_width, multiple)
        scaled_height = ScalingUtils.scale_int(height, rounding_mode_height, scale_factor_height, multiple)

        # Ensure we have valid dimensions
        temp_width = scaled_width if scaled_width is not None else width
        temp_height = scaled_height if scaled_height is not None else height

        # Ensure dimensions are valid for latent space (divisible by 8)
        temp_width = max(8, temp_width)
        temp_height = max(8, temp_height)

        # Apply overrides if set
        final_width = width_override if width_override > 0 else temp_width
        final_height = height_override if height_override > 0 else temp_height

        # Create latent tensor
        latent = torch.zeros([batch_size, 4, final_height // 8, final_width // 8], device=self.device)

        return (
            {"samples": latent},
            final_width,
            final_height,
        )
