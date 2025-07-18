import numpy as np  # type: ignore
import torch  # type: ignore
import torch.nn.functional as F  # type: ignore

from .shared.ryuu_log import ryuu_log
from .shared.scaling_utils import ScalingUtils


class ScaleToMultipleBase:
    """
    Base class for scaling image dimensions and/or integers to a specified multiple.
    """

    # May be overridden by child classes
    ALLOW_SEPARATE_ROUNDING_MODES = False
    ALLOW_SEPARATE_SCALE_FACTORS = False

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("scaled_image", "scaled_width", "scaled_height")
    FUNCTION = "main_operation"
    CATEGORY = "RyuuNoodles/Utils"

    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "optional": {
                "image": (
                    "IMAGE",
                    {
                        "tooltip": (
                            "Image to scale. If not provided, only width and height will be scaled. "
                            "If either or both of the optional width/height inputs are provided, the resizing will use the given input(s)."
                        ),
                    },
                ),
                "width": (
                    "INT",
                    {
                        "default": None,
                        "min": 1,
                        "forceInput": True,
                        "tooltip": (
                            "Optional width to scale the image to after the multiple scaling.\n"
                            "If no image is provided it will still output the scaled number."
                        ),
                    },
                ),
                "height": (
                    "INT",
                    {
                        "default": None,
                        "min": 1,
                        "forceInput": True,
                        "tooltip": (
                            "Optional height to scale the image to after the multiple scaling.\n"
                            "If no image is provided it will still output the scaled number."
                        ),
                    },
                ),
            },
            "required": {
                "multiple": (
                    "INT",
                    {
                        "default": 64,
                        "min": 1,
                        "tooltip": ("Multiple to scale to.\n Setting to 1 effectively disables this."),
                    },
                ),
                "crop_mode": (
                    ["stretch", "center", "fill", "uniform", "uniform fill"],
                    {
                        "default": "stretch",
                        "tooltip": (
                            "Crop mode for the image. \n"
                            "'stretch' will stretch the image to fill the target dimensions.\n"
                            "'center' will center the image in the target dimensions.\n"
                            "'fill' will scale the image to fill the target dimensions while maintaining aspect ratio, cropping if necessary.\n"
                            "'uniform' will scale the image to fit within the target dimensions while maintaining aspect ratio.\n"
                            "'uniform fill' will scale the image to fill the target dimensions while maintaining aspect ratio, adding padding if necessary."
                        ),
                    },
                ),
                "resize_mode": (
                    [
                        "lanczos",
                        "nearest",
                        "bilinear",
                        "bicubic",
                        "box",
                        "hamming",
                        "bilinear - tensor",
                    ],
                    {
                        "default": "lanczos",
                        "tooltip": (
                            "Resize mode for the image.\n"
                            "'bilinear - tensor' is different from normal bilinear, it will use "
                            "torch.nn.functional.interpolate() to resize the image and look very different from normal bilinear."
                        ),
                    },
                ),
            },
        }
        # "img_use_opt_res": (
        #     "BOOLEAN",
        #     {
        #         "default": False,
        #         "tooltip": (
        #             "By default the image will be resized by using it's own dimensions (width/height).\n"
        #             "If this setting is set to 'True' then the image will be resized based on the optional "
        #             "width and height (so far they are given). In the case where this setting is 'True' "
        #             "but neither or only one out of the two is given, the missing number will be substituted "
        #             "using the image's own width and/or height."
        #         ),
        #     },
        # ),

        # Add rounding mode inputs based on flags
        inputs["required"].update(
            ScalingUtils.create_rounding_mode_inputs(separate_modes=cls.ALLOW_SEPARATE_ROUNDING_MODES)
        )

        # Add scale factor inputs based on flags
        inputs["required"].update(
            ScalingUtils.create_scale_factor_inputs(separate_factors=cls.ALLOW_SEPARATE_SCALE_FACTORS)
        )

        return inputs

    def _create_placeholder_image(self, width, height):
        # Create a placeholder image if no input image is provided
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            ryuu_log(
                "PIL or numpy not found. Cannot create a placeholder image. Returning a black tensor.",
                loglevel="warning",
            )
            return torch.zeros((1, height, width, 3), dtype=torch.float32)

        img = Image.new("RGB", (width, height), "black")
        draw = ImageDraw.Draw(img)
        text = "No Image"
        font = None
        font_names = [
            "arial.ttf",  # Common on Windows and macOS
            "DejaVuSans.ttf",  # Common on Linux
            "LiberationSans-Regular.ttf",  # Common on Linux
            "Verdana.ttf",  # Common on Windows
            "Helvetica.dfont",  # Common on macOS
            "FreeSans.ttf",  # Common on Linux
        ]
        for font_name in font_names:
            try:
                font = ImageFont.truetype(font_name, size=40)
                break  # Font found, exit loop
            except IOError:
                continue  # Font not found, try next

        if font is None:
            # If no fonts from the list are found, fall back to the default
            font = ImageFont.load_default()

        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2
        draw.text((text_x, text_y), text, fill="white", font=font)

        np_image = np.array(img, dtype=np.float32) / 255.0
        tensor_image = torch.from_numpy(np_image).unsqueeze(0)
        return tensor_image

    def _pil_resize(self, image, target_h, target_w, mode):
        from PIL import Image

        mode_map = {
            "lanczos": Image.Resampling.LANCZOS,
            "nearest": Image.Resampling.NEAREST,
            "bilinear": Image.Resampling.BILINEAR,
            "bicubic": Image.Resampling.BICUBIC,
            "box": Image.Resampling.BOX,
            "hamming": Image.Resampling.HAMMING,
        }
        resample = mode_map.get(mode, Image.Resampling.BILINEAR)
        b, h, w, c = image.shape
        image_np = image.cpu().numpy()
        out = []
        for i in range(b):
            img = (image_np[i] * 255).clip(0, 255).astype(np.uint8)
            pil_img = Image.fromarray(img)
            pil_resized = pil_img.resize((target_w, target_h), resample=resample)
            arr = np.asarray(pil_resized).astype(np.float32) / 255.0
            out.append(arr)
        out = np.stack(out, axis=0)
        return torch.from_numpy(out).to(image.device)

    def _tensor_resize(self, image, target_h, target_w):
        img_bchw = image.permute(0, 3, 1, 2)
        resized = F.interpolate(img_bchw, size=(target_h, target_w), mode="bilinear", align_corners=False)
        return resized.permute(0, 2, 3, 1)

    def _process_scaling(
        self,
        image,
        width,
        height,
        multiple,
        rounding_mode_width,
        rounding_mode_height,
        scale_factor_width,
        scale_factor_height,
        crop_mode,
        resize_mode,
    ):
        # if image, width and height are all None, raise error
        if image is None and width is None and height is None:
            raise ValueError(
                "At least one of 'image', 'width', or 'height' must be provided. "
                "Please provide at least one of these inputs."
            )

        # Use image dimensions if width/height not provided but image is
        if width is None and image is not None:
            ryuu_log(
                "ScaleToMultiple: Width is None but image is provided, using image width for scaling.",
                loglevel="info",
            )
            width = image.shape[2]
        if height is None and image is not None:
            ryuu_log(
                "ScaleToMultiple: Height is None but image is provided, using image height for scaling.",
                loglevel="info",
            )
            height = image.shape[1]

        scaled_width = ScalingUtils.scale_int(width, rounding_mode_width, scale_factor_width, multiple)
        scaled_height = ScalingUtils.scale_int(height, rounding_mode_height, scale_factor_height, multiple)

        if image is None:
            # No image: return placeholder image with scaled dimensions
            final_w = scaled_width if scaled_width is not None else 128
            final_h = scaled_height if scaled_height is not None else 128
            scaled_image = self._create_placeholder_image(final_w, final_h)
            return (scaled_image, final_w, final_h)

        orig_h, orig_w = image.shape[1:3]
        final_w = scaled_width if scaled_width is not None else orig_w
        final_h = scaled_height if scaled_height is not None else orig_h

        if orig_w == final_w and orig_h == final_h:
            # No scaling needed
            return (image, final_w, final_h)

        use_tensor = resize_mode == "bilinear - tensor"
        pil_mode = resize_mode if resize_mode != "bilinear - tensor" else "bilinear"

        def resize_func(img, h, w):
            if use_tensor:
                return self._tensor_resize(img, h, w)
            else:
                return self._pil_resize(img, h, w, pil_mode)

        img_bchw = image.permute(0, 3, 1, 2)  # BHWC -> BCHW
        resized_bchw = None

        if crop_mode == "stretch":
            scaled_image = resize_func(image, final_h, final_w)
            return (scaled_image, final_w, final_h)
        else:
            orig_aspect = orig_w / orig_h
            target_aspect = final_w / final_h

            if crop_mode == "center":
                # Center image on canvas, no scaling
                canvas = torch.zeros(
                    (img_bchw.shape[0], img_bchw.shape[1], final_h, final_w), device=image.device, dtype=image.dtype
                )
                paste_x = (final_w - orig_w) // 2
                paste_y = (final_h - orig_h) // 2
                src_x_start, src_y_start = max(0, -paste_x), max(0, -paste_y)
                src_x_end, src_y_end = min(orig_w, final_w - paste_x), min(orig_h, final_h - paste_y)
                dst_x_start, dst_y_start = max(0, paste_x), max(0, paste_y)
                dst_x_end, dst_y_end = min(final_w, orig_w + paste_x), min(final_h, orig_h + paste_y)

                if src_x_end > src_x_start and src_y_end > src_y_start:
                    canvas[:, :, dst_y_start:dst_y_end, dst_x_start:dst_x_end] = img_bchw[
                        :, :, src_y_start:src_y_end, src_x_start:src_x_end
                    ]
                resized_bchw = canvas
            else:  # uniform, uniform fill, fill
                # For "uniform" and "uniform fill", both fit the image inside the target while preserving aspect ratio and pad if needed.
                # For "fill", scale to cover and crop if needed.
                if crop_mode in ["uniform", "uniform fill"]:  # Fit (pad)
                    resize_w, resize_h = (
                        (final_w, round(final_w / orig_aspect))
                        if orig_aspect > target_aspect
                        else (round(final_h * orig_aspect), final_h)
                    )
                else:  # Fill (crop)
                    resize_w, resize_h = (
                        (round(final_h * orig_aspect), final_h)
                        if orig_aspect > target_aspect
                        else (final_w, round(final_w / orig_aspect))
                    )

                resize_w, resize_h = max(1, resize_w), max(1, resize_h)
                temp_resized = resize_func(image, resize_h, resize_w)
                temp_bchw = temp_resized.permute(0, 3, 1, 2)

                if crop_mode in ["uniform", "uniform fill"]:
                    # Place resized image on black canvas (padding)
                    canvas = torch.zeros(
                        (img_bchw.shape[0], img_bchw.shape[1], final_h, final_w), device=image.device, dtype=image.dtype
                    )
                    paste_x, paste_y = (final_w - resize_w) // 2, (final_h - resize_h) // 2
                    canvas[:, :, paste_y : paste_y + resize_h, paste_x : paste_x + resize_w] = temp_bchw
                    resized_bchw = canvas
                else:  # fill
                    # Crop center region to target size
                    crop_x, crop_y = (resize_w - final_w) // 2, (resize_h - final_h) // 2
                    resized_bchw = temp_bchw[:, :, crop_y : crop_y + final_h, crop_x : crop_x + final_w]

        scaled_image = resized_bchw.permute(0, 2, 3, 1)  # BCHW -> BHWC
        return (scaled_image, final_w, final_h)

    def main_operation(self, **kwargs):
        """Main operation that handles parameter extraction based on class flags."""
        # Extract common parameters
        image = kwargs.get("image")
        width = kwargs.get("width")
        height = kwargs.get("height")
        multiple = kwargs["multiple"]
        crop_mode = kwargs["crop_mode"]
        resize_mode = kwargs["resize_mode"]

        # Extract rounding mode and scale factor parameters based on flags
        rounding_mode_width, rounding_mode_height, scale_factor_width, scale_factor_height = (
            ScalingUtils.extract_scaling_params(
                kwargs,
                separate_modes=self.ALLOW_SEPARATE_ROUNDING_MODES,
                separate_factors=self.ALLOW_SEPARATE_SCALE_FACTORS,
            )
        )

        return self._process_scaling(
            image,
            width,
            height,
            multiple,
            rounding_mode_width,
            rounding_mode_height,
            scale_factor_width,
            scale_factor_height,
            crop_mode,
            resize_mode,
        )
