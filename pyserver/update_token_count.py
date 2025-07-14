import re
import warnings

from aiohttp import web
from transformers import AutoTokenizer, CLIPTokenizer, T5Tokenizer, T5TokenizerFast

from server import PromptServer  # type: ignore

from ..modules.shared.ryuu_log import ryuu_log

INCLUDE_TOKENS = False

routes = PromptServer.instance.routes

# Lazy tokenizer loader and cache
_tokenizer_cache = {}


def load_and_log(tokenizer_cls, *args, log_name=None, **kwargs):
    if log_name:
        ryuu_log(f"Loading {log_name} tokenizer...", loglevel="debug")
    tok = tokenizer_cls.from_pretrained(*args, **kwargs)
    if log_name:
        ryuu_log(f"Loaded {log_name} tokenizer.", loglevel="debug")
    return tok


def get_tokenizer(name):
    key = name.lower().strip()
    if key in _tokenizer_cache:
        return _tokenizer_cache[key]
    if key == "clip_l":  # CLIP-L | SDXL, FLUX (2nd), SD3(.5), etc
        # NOTE: CLIP-L Fast tokenizer is NOT faster
        # NOTE: Jina clip probably same as this (or clip G)
        tok = load_and_log(CLIPTokenizer, "openai/clip-vit-large-patch14", log_name="CLIP-L")

    # CLIP-G tok is practically almost exact same as CLIP-L tok
    # not important but, CLIP-G (pretty sure it just has '!' as padding token over L) https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/tree/main/tokenizer_2
    # elif key == "clip_g":  # CLIP-G | SDXL, SD3(.5), etc
    #     tok = load_and_log(
    #         CLIPTokenizer, "stabilityai/stable-diffusion-xl-base-1.0", subfolder="tokenizer_2", log_name="CLIP-G"
    #     )

    # NOTE: below are LLM tokenizers, most output same or very similar token counts but they are NOT the same
    elif key == "t5":  # T5-XXL | Chroma, Flux (1st), SD3(.5), etc
        # # NOTE: BFL flux dev is also possible, but they should all do the same thing because same spiece.model file iirc
        tok = load_and_log(T5Tokenizer, "google/t5-v1_1-xxl", log_name="T5", legacy=False)
    elif key == "t5_fast":  # T5-XXL | Faster | Flux (1st), SD3(.5), etc
        tok = load_and_log(T5TokenizerFast, "google/t5-v1_1-xxl", log_name="T5-Fast", legacy=False)
        # legacy=False shouldnt impact anything, ref: https://github.com/huggingface/transformers/pull/24565
    elif key == "umt5":  # umt5-XXL | WAN 2.1
        tok = load_and_log(AutoTokenizer, "google/umt5-xxl", log_name="UMT5")
    elif key == "gemma2":  # Gemma 2 2B | Lumina Image 2.0
        tok = load_and_log(AutoTokenizer, "unsloth/gemma-2-2b", log_name="Gemma2")
    elif key == "gemma3":  # Gemma 3 1B/4B | *Custom* | NOTE: VERY similar to G2 but not same.
        tok = load_and_log(AutoTokenizer, "unsloth/gemma-3-1b-it", log_name="Gemma3")
    elif key == "llama3":  # LLaMA 3.1 8B | hidream, hunyuan video, etc
        tok = load_and_log(AutoTokenizer, "unsloth/Meta-Llama-3.1-8B-Instruct", log_name="LLaMA3")
    elif key == "qwen25vl" or key == "qwen2.5vl":  # Qwen 2.5 VL | OmnigenV2
        tok = load_and_log(AutoTokenizer, "Qwen/Qwen2.5-VL-3B-Instruct", log_name="LLaMA3")
    elif key == "auraflow":  # Pile T5 me thinks | AuraFlow/PonyFlow (Pony v7)
        tok = load_and_log(AutoTokenizer, "fal/AuraFlow", subfolder="tokenizer", log_name="AuraFlow")
    else:
        tok = None
    _tokenizer_cache[key] = tok
    return tok


# todo: allow adding through config file or something, so users can add their own tokenizers
# related todo in tokenCounter.Overlayjs file


# Helper function to strip weighting syntax from the text
# (word), (word:1.2), ((word:1.2):0.5) etc. is handled
# escaped parentheses like \(word\) becomes (word)
def strip_weighting(text):
    # Placeholders for escaped parentheses using Unicode private use area
    open_paren_placeholder = "\ue000"
    close_paren_placeholder = "\ue001"

    # Process escape characters and replace escaped parentheses
    processed_text = []
    escaped = False
    for char in text:
        if escaped:
            if char == "(":
                processed_text.append(open_paren_placeholder)
            elif char == ")":
                processed_text.append(close_paren_placeholder)
            else:
                # Keep the backslash and the char if it wasn't ( or )
                processed_text.append("\\")
                processed_text.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        else:
            processed_text.append(char)

    # Handle trailing escape character if any
    if escaped:
        processed_text.append("\\")

    text = "".join(processed_text)

    # Regex to find the innermost parentheses (and weight if given)
    # Matches (content) or (content:weight) where content has no parentheses
    # Weight format allows for positive/negative numbers, integers, and decimals
    innermost_pattern = re.compile(r"\(([^()]*?)(?::[-+]?\d*(?:\.\d+)?)?\)")

    # Iteratively replace innermost patterns until no changes occur
    previous_text = None
    while text != previous_text:
        previous_text = text
        text = innermost_pattern.sub(r"\1", text)  # Replace with content only

    # Replace placeholders back to literal parentheses
    text = text.replace(open_paren_placeholder, "(")
    text = text.replace(close_paren_placeholder, ")")

    return text


def handle_clip_l_breaks(text, tokenizer, add_special_tokens=False):
    """Handle BREAK keywords for CLIP-L tokenizer with 75-token chunking"""
    if "BREAK" not in text:
        # No BREAK found, tokenize normally
        outputs = tokenizer(text, return_tensors="pt", add_special_tokens=add_special_tokens)
        return outputs["input_ids"].shape[1]

    # Split text by BREAK and process each chunk
    # Handles BREAK at start, end, or surrounded by any whitespace
    chunks = re.split(r"(?<!\w)BREAK(?!\w)", text)
    total_tokens = 0

    for i, chunk in enumerate(chunks):
        # Tokenize the current chunk
        outputs = tokenizer(chunk, return_tensors="pt", add_special_tokens=add_special_tokens)
        chunk_tokens = outputs["input_ids"].shape[1]

        # For all but the last chunk, always count as a full 75-token chunk
        if i < len(chunks) - 1:
            total_tokens += 75
        else:
            total_tokens += chunk_tokens

    return total_tokens


@routes.post("/ryuu/update_token_count")
async def update_token_count(request):
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    text = data.get("text", "")
    tok_types = data.get("tok_types") or []
    if not text:
        return web.json_response({"error": "No text provided"}, status=400)

    add_special_tokens = data.get("add_special_tokens", False)

    text = strip_weighting(text)

    token_counts = {}
    tokens_map = {}

    for name in tok_types:
        tokenizer = get_tokenizer(name)
        if tokenizer is None:
            token_counts[name] = None
            if INCLUDE_TOKENS:
                tokens_map[name] = []
            continue

        # Special handling for CLIP-L tokenizer with BREAK keywords
        if name.lower().strip() == "clip_l" and data.get("support_break_keyword", False):
            num = handle_clip_l_breaks(text, tokenizer, add_special_tokens)
        else:
            # Standard tokenization for other tokenizers
            outputs = tokenizer(text, return_tensors="pt", add_special_tokens=add_special_tokens)
            num = outputs["input_ids"].shape[1]

        token_counts[name] = num

        if INCLUDE_TOKENS:
            # return the raw token strings too
            # NOTE: unused in JS currently
            # For CLIP-L with BREAK, this won't show the padding tokens, just the actual text tokens
            outputs = tokenizer(text.replace("BREAK", ""), return_tensors="pt", add_special_tokens=add_special_tokens)
            ids = outputs["input_ids"][0]
            tokens_map[name] = [tokenizer.convert_ids_to_tokens(int(t)) for t in ids]

    # build response
    resp_data = {"token_counts": token_counts}
    if INCLUDE_TOKENS:
        resp_data["tokens"] = tokens_map

    return web.json_response(resp_data)
