# Code is from https://github.com/kijai/ComfyUI-KJNodes
# Licensed GPL-3.0


import torch

from ..modules.shared.ryuu_log import ryuu_log


class ColorMatch:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_target": ("IMAGE",),
                "image_ref": ("IMAGE",),
                "method": (
                    [
                        "mkl",
                        "hm",
                        "reinhard",
                        "mvgd",
                        "hm-mvgd-hm",
                        "hm-mkl-hm",
                    ],
                    {
                        "default": "mkl",
                        "tooltip": (
                            "Color transfer method to use. "
                            "I personally like 'mkl' most because it transfers colors well with least 'artifacts' "
                            "in scenarios where both input images are structually the same or very close to same."
                        ),
                    },
                ),
            },
            "optional": {
                "strength": ("FLOAT", {"default": 0.97, "min": 0.0, "max": 10.0, "step": 0.005}),
            },
        }

    CATEGORY = "RyuuNoodles 🐲/Images"

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "colormatch"
    DESCRIPTION = """
This is the same Color Match node as from https://github.com/kijai/ComfyUI-KJNodes except that it is modified to be bypass friendly
so that during bypass, the target image will be passed through rather than the reference image.

color-matcher enables color transfer across images which comes in handy for automatic
color-grading of photographs, paintings and film sequences as well as light-field
and stopmotion corrections.

The methods behind the mappings are based on the approach from Reinhard et al.,
the Monge-Kantorovich Linearization (MKL) as proposed by Pitie et al. and our analytical solution
to a Multi-Variate Gaussian Distribution (MVGD) transfer in conjunction with classical histogram
matching. As shown below our HM-MVGD-HM compound outperforms existing methods.
https://github.com/hahnec/color-matcher/

"""

    def colormatch(self, image_target, image_ref, method, strength=1.0):
        try:
            from color_matcher import ColorMatcher
        except:
            raise Exception(
                "Can't import color-matcher, did you install requirements.txt? Manual install: pip install color-matcher"
            )
        cm = ColorMatcher()
        image_ref = image_ref.cpu()
        image_target = image_target.cpu()
        batch_size = image_target.size(0)
        out = []
        images_target = image_target.squeeze()
        images_ref = image_ref.squeeze()

        image_ref_np = images_ref.numpy()
        images_target_np = images_target.numpy()

        if image_ref.size(0) > 1 and image_ref.size(0) != batch_size:
            raise ValueError("ColorMatch: Use either single reference image or a matching batch of reference images.")

        for i in range(batch_size):
            image_target_np = images_target_np if batch_size == 1 else images_target[i].numpy()
            image_ref_np_i = image_ref_np if image_ref.size(0) == 1 else images_ref[i].numpy()

            try:
                image_result = cm.transfer(src=image_target_np, ref=image_ref_np_i, method=method)
            except BaseException as e:
                ryuu_log(f"Error occurred during transfer: {e}")
                break

            # Apply the strength multiplier
            image_result = image_target_np + strength * (image_result - image_target_np)
            out.append(torch.from_numpy(image_result))

        out = torch.stack(out, dim=0).to(torch.float32)
        out.clamp_(0, 1)
        return (out,)
