# Code is from https://github.com/kijai/ComfyUI-KJNodes
# Licensed GPL-3.0


import numpy as np
import torch

from comfy_api.latest import io

from ..modules.shared.ryuu_log import ryuu_log


class ColorMatch(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Ryuu_ColorMatch",
            display_name="Color Match 🐲",
            category="RyuuNoodles 🐲/Images",
            description="""
This is the nearly same Color Match node as from https://github.com/kijai/ComfyUI-KJNodes except that it is modified to be bypass friendly
so that during bypass, the target image will be passed through rather than the reference image. 
(Other changes: Multithreading is missing and images are in fp64 tensors instead of fp32 for really high-res images.)

color-matcher enables color transfer across images which comes in handy for automatic
color-grading of photographs, paintings and film sequences as well as light-field
and stopmotion corrections.

The methods behind the mappings are based on the approach from Reinhard et al.,
the Monge-Kantorovich Linearization (MKL) as proposed by Pitie et al. and our analytical solution
to a Multi-Variate Gaussian Distribution (MVGD) transfer in conjunction with classical histogram
matching. As shown below our HM-MVGD-HM compound outperforms existing methods.
https://github.com/hahnec/color-matcher/

""",  # noqa: W291
            inputs=[
                io.Image.Input(name="image_target", description="Target image to apply color transfer to."),
                io.Image.Input(name="image_ref", description="Reference image to take colors from."),
                io.Combo.Input(
                    options=["mkl", "hm", "reinhard", "mvgd", "hm-mvgd-hm", "hm-mkl-hm"],
                    name="method",
                    default="mkl",
                    description=(
                        "Color transfer method to use. "
                        "I personally like 'mkl' most because it transfers colors well with least 'artifacts' "
                        "in scenarios where both input images are structually the same or very close to same."
                    ),
                ),
                io.Float.Input(
                    name="strength",
                    default=1.0,
                    min=0.0,
                    max=10.0,
                    step=0.005,
                    description="Strength of the color transfer effect.",
                ),
            ],
            outputs=[
                io.Image.Output(name="image", description="Image after color transfer."),
            ],
        )

    @classmethod
    def execute(cls, image_target, image_ref, method, strength) -> io.NodeOutput:
        try:
            from color_matcher import ColorMatcher
        except:
            raise Exception(
                "[RyuuNoodles Color Match] Can't import color-matcher, were the custom nodes installed correctly?"
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
            raise ValueError(
                "[RyuuNoodles Color Match] Use either single reference image or a matching batch of reference images."
            )

        for i in range(batch_size):
            image_target_np_i = images_target_np if batch_size == 1 else images_target[i].numpy()
            image_ref_np_i = image_ref_np if image_ref.size(0) == 1 else images_ref[i].numpy()

            try:
                # Convert data to float64 for the library
                target_f64 = image_target_np_i.astype(np.float64)
                ref_f64 = image_ref_np_i.astype(np.float64)
                image_result = cm.transfer(src=target_f64, ref=ref_f64, method=method)
            except BaseException as e:
                ryuu_log(f"[Color Match] Error occurred during transfer: {e}", loglevel="error")
                break

            # Apply the strength multiplier
            image_result = target_f64 + strength * (image_result - target_f64)
            out.append(torch.from_numpy(image_result))

        # in case the loop breaks on first item
        if not out:
            return (image_target,)

        out = torch.stack(out, dim=0).to(torch.float32)
        out.clamp_(0, 1)

        return io.NodeOutput(out)
