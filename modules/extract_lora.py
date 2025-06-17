import json
import os
from enum import Enum

import torch  # type: ignore

import comfy.model_management  # type: ignore
import comfy.utils  # type: ignore
import folder_paths  # type: ignore
from comfy.cli_args import args  # type: ignore

from ..modules.shared.ryuu_log import ryuu_log

CLAMP_QUANTILE = 0.99


class LORAType(Enum):
    STANDARD = 0
    FULL_DIFF = 1


LORA_TYPES = {"standard": LORAType.STANDARD, "full_diff": LORAType.FULL_DIFF}


def extract_lora(diff, rank):
    conv2d = len(diff.shape) == 4
    kernel_size = None if not conv2d else diff.size()[2:4]
    conv2d_3x3 = conv2d and kernel_size != (1, 1)
    out_dim, in_dim = diff.size()[0:2]
    rank = min(rank, in_dim, out_dim)

    if conv2d:
        if conv2d_3x3:
            diff = diff.flatten(start_dim=1)
        else:
            diff = diff.squeeze()

    U, S, Vh = torch.linalg.svd(diff.float())
    U = U[:, :rank]
    S = S[:rank]
    U = U @ torch.diag(S)
    Vh = Vh[:rank, :]

    dist = torch.cat([U.flatten(), Vh.flatten()])
    hi_val = torch.quantile(dist, CLAMP_QUANTILE)
    low_val = -hi_val

    U = U.clamp(low_val, hi_val)
    Vh = Vh.clamp(low_val, hi_val)
    if conv2d:
        U = U.reshape(out_dim, rank, 1, 1)
        Vh = Vh.reshape(rank, in_dim, kernel_size[0], kernel_size[1])
    return (U, Vh)


def _check_text_encoder_diff(text_encoder_diff):
    """
    Returns two booleans: any_diff_zero, text_projection_diff_zero
    """
    sd = text_encoder_diff.patcher.model_state_dict(filter_prefix="")
    any_diff_zero = False
    text_proj_zero = False
    for k, diff in sd.items():
        if k.endswith(".weight"):
            if diff.abs().sum().item() == 0:
                ryuu_log("[Extract and Save LoRA] No weight difference for key %s", k)
                any_diff_zero = True
                if k.endswith("transformer.text_projection.weight"):
                    text_proj_zero = True
    ryuu_log(
        "[Extract and Save LoRA] Text encoder any_diff_zero=%s, text_projection_diff_zero=%s",
        any_diff_zero,
        text_proj_zero,
    )
    return any_diff_zero, text_proj_zero


def calc_lora_model(model_diff, rank, prefix_model, prefix_lora, output_sd, lora_type, bias_diff=False):
    comfy.model_management.load_models_gpu([model_diff], force_patch_weights=True)
    sd = model_diff.model_state_dict(filter_prefix=prefix_model)

    for k in sd:
        if k.endswith(".weight"):
            weight_diff = sd[k]
            if lora_type == LORAType.STANDARD:
                if weight_diff.ndim < 2:
                    if bias_diff:
                        output_sd[f"{prefix_lora}{k[len(prefix_model):-7]}.diff"] = (
                            weight_diff.contiguous().half().cpu()
                        )
                    continue
                try:
                    out = extract_lora(weight_diff, rank)
                    output_sd[f"{prefix_lora}{k[len(prefix_model):-7]}.lora_up.weight"] = (
                        out[0].contiguous().half().cpu()
                    )
                    output_sd[f"{prefix_lora}{k[len(prefix_model):-7]}.lora_down.weight"] = (
                        out[1].contiguous().half().cpu()
                    )
                except:
                    ryuu_log(
                        "[Extract and Save LoRA] Could not generate lora weights for key %s, is the weight difference a zero?",
                        k,
                    )
            elif lora_type == LORAType.FULL_DIFF:
                output_sd[f"{prefix_lora}{k[len(prefix_model):-7]}.diff"] = weight_diff.contiguous().half().cpu()

        elif bias_diff and k.endswith(".bias"):
            output_sd[f"{prefix_lora}{k[len(prefix_model):-5]}.diff_b"] = sd[k].contiguous().half().cpu()
    return output_sd


class ExtractAndSaveLora:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "filename_prefix": ("STRING", {"default": "loras/ComfyUI_extracted_lora"}),
                "filename_suffix": (
                    "STRING",
                    {
                        "default": "{counter:05}",
                        "tooltip": (
                            "Suffix to append to the filename. Will be appended after '_noTE', '_biasdiff', etc. "
                            "Use {counter} for a counter, it supports zero padding (E.g.: test_{counter:05}_ = test_00001_)."
                        ),
                    },
                ),
                "rank": (
                    "INT",
                    {
                        "default": 16,
                        "min": 1,
                        "max": 4096,
                        "step": 1,
                        "tooltip": (
                            "LoRA network dimension size (LoRA Rank). "
                            "Prefer 16-64 depending on how much data you want to have "
                            "saved in relation to the checkpoint differences."
                        ),
                    },
                ),
                "lora_type": (
                    tuple(LORA_TYPES.keys()),
                    {
                        "tooltip": (
                            "Type of LoRA to extract. Standard is the default "
                            "(like normal trained LoRA; rank 32 ~= 217mb LoRA assuming TE diff is extracted too), "
                            "full_diff saves the full weight diff (very large)."
                        ),
                    },
                ),
                "bias_diff": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": (
                            "If enabled, includes .bias weight differences in the extracted LoRA. "
                            "This can help match the original model behavior more closely, with minimal impact on file size."
                        ),
                    },
                ),
                "skip_on_any_diff_zero": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": ("If True, skips saving the text encoder weights if any weight diff is zero."),
                    },
                ),
                "skip_on_proj_diff_zero": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": (
                            "If True, skips saving the text encoder weights if 'text_projection.weight' diff is zero."
                        ),
                    },
                ),
                "embed_workflow": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": (
                            "Enable or disable saving of workflow inside the LoRA metadata. "
                            "Will not save metadata if it's disabled in ComfyUI globally."
                        ),
                    },
                ),
            },
            "optional": {
                "model_diff": (
                    "MODEL",
                    {
                        "tooltip": ("The ModelSubtract output to be converted to a lora."),
                    },
                ),
                "text_encoder_diff": (
                    "CLIP",
                    {
                        "tooltip": ("The CLIPSubtract output to be converted to a lora."),
                    },
                ),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ()
    FUNCTION = "extract_and_save"
    OUTPUT_NODE = True
    EXPERIMENTAL = True
    CATEGORY = "RyuuNoodles 🐲/Utils"
    DESCRIPTION = (
        "Saves the model and text encoder diffs as LoRA weights in .safetensors format. \n"
        "How is this different from the built-in Extract and Save LoRA node? \n"
        "This one allows you choose not to save text encoder weights if any text encoder key difference is 0 "
        "or if the sepcific *.transformers.text_projection.weight key is 0. \n"
        "It also allows you to choose file suffix, and adds keywords to the "
        "filename like r40 to indicate rank size, _TE / _noTE to indicate if the text encoder diff was included, and "
        "_biasdiff to indicate that bias differences were included.\n"
        "Workflow can also be saved by embedding it into the LoRA's metadata.\n\n"
        "It's possible this node doesn't quite work for the TE saving and all that, "
        "I've had unexpectedly mixed result for the same extracts when there shouldn't have been any nuance."
    )

    def extract_and_save(
        self,
        filename_prefix,
        filename_suffix,
        rank,
        lora_type,
        bias_diff,
        skip_on_any_diff_zero,
        skip_on_proj_diff_zero,
        embed_workflow,
        # optional
        model_diff=None,
        text_encoder_diff=None,
        # hidden, for metadata saving
        prompt=None,
        extra_pnginfo=None,
    ):
        if model_diff is None and text_encoder_diff is None:
            return {}

        lora_type = LORA_TYPES.get(lora_type)
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir
        )

        output_sd = {}
        # Process model diffs
        if model_diff is not None:
            output_sd = calc_lora_model(
                model_diff, rank, "diffusion_model.", "diffusion_model.", output_sd, lora_type, bias_diff=bias_diff
            )

        # Process text encoder diffs with skip logic
        has_te_diff = False
        if text_encoder_diff is not None:
            any_zero, proj_zero = _check_text_encoder_diff(text_encoder_diff)
            skip = (skip_on_any_diff_zero and any_zero) or (skip_on_proj_diff_zero and proj_zero)
            if skip:
                ryuu_log(
                    "[Extract and Save LoRA] Skipping text encoder diff inclusion (any_zero=%s, proj_zero=%s)",
                    any_zero,
                    proj_zero,
                )
            else:
                output_sd = calc_lora_model(
                    text_encoder_diff.patcher,
                    rank,
                    "",
                    "text_encoders.",
                    output_sd,
                    lora_type,
                    bias_diff=bias_diff,
                )
                has_te_diff = True

        # check if extracted lora has text encoder diff in it or biasdiff enabled
        has_te = "_TE" if has_te_diff else "_noTE"
        has_biasdiff = "_biasdiff" if bias_diff else "_nobiasdiff"

        # region metadata
        prompt_info = ""
        if prompt is not None:
            prompt_info = json.dumps(prompt)

        metadata = {}
        if not args.disable_metadata and embed_workflow:
            metadata["prompt"] = prompt_info
            if extra_pnginfo is not None:
                for x in extra_pnginfo:
                    metadata[x] = json.dumps(extra_pnginfo[x])
        # endregion

        formatted_suffix = filename_suffix.format(counter=counter)
        formatted_suffix = f"_{formatted_suffix}" if (not filename_suffix == "") else ""

        output_checkpoint = f"{filename}_r{rank}{has_te}{has_biasdiff}{formatted_suffix}.safetensors"
        output_checkpoint = os.path.join(full_output_folder, output_checkpoint)

        comfy.utils.save_torch_file(output_sd, output_checkpoint, metadata=metadata)
        return {}
