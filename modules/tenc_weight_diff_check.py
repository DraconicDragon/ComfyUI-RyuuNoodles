from ..modules.utils.ryuu_print import ryuu_print


class TextEncoderDiffCheck:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_encoder_diff": (
                    "CLIP",
                    {"tooltip": "The e.g.: CLIPSubtract output to check"},
                ),
            }
        }

    RETURN_TYPES = ("CLIP", "BOOLEAN", "BOOLEAN")
    RETURN_NAMES = ("text_encoder_diff", "any_diff_zero", "text_projection_diff_zero")
    FUNCTION = "check"
    OUTPUT_NODE = True
    CATEGORY = "Utils"
    DESCRIPTION = (
        "Checks if the text encoder diff is zero for any weight and specifically for *.transformer.text_projection.weight. \n"
        "Outputs a booleans indicating if any weight is zero and another boolean for the text projection weight."
    )

    def check(self, text_encoder_diff):
        sd = text_encoder_diff.patcher.model_state_dict(filter_prefix="")

        any_diff_zero = False
        text_projection_diff_zero = False

        for k, diff in sd.items():
            if k.endswith(".weight"):
                if diff.abs().sum().item() == 0:
                    ryuu_print("No weight difference for key %s", k)
                    any_diff_zero = True
                    if k.endswith("transformer.text_projection.weight"):
                        text_projection_diff_zero = True

        ryuu_print(f"[TextEncoderDiffCheck] any_diff_zero = {any_diff_zero}")
        ryuu_print(f"[TextEncoderDiffCheck] text_projection_diff_zero = {text_projection_diff_zero}")

        return {
            "text_encoder_diff": text_encoder_diff,
            "any_diff_zero": any_diff_zero,
            "text_projection_diff_zero": text_projection_diff_zero,
        }
