from aiohttp import web
from server import PromptServer
from transformers import AutoTokenizer, CLIPTokenizer, T5Tokenizer, T5TokenizerFast

# load once at module load

# CLIP-L, SDXL, FLUX (2nd), SD3(.5), etc
clip_l_tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")  # NOTE: fast version isnt faster

# CLIP-G
# clip_g_tokenizer = CLIPTokenizer.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", subfolder="tokenizer_2")

# NOTE: BFL flux dev is also possible, but they should all do the same thing because same spiece.model file iirc
t5_tokenizer = T5Tokenizer.from_pretrained("google/t5-v1_1-xxl")

t5_tokenizer_fast = T5TokenizerFast.from_pretrained("google/t5-v1_1-xxl")  # its faster, but idk otherwise
# todo: consider using google-t5/t5-small?

# UMT5 XXL, WAN2.1
umt5_tokenizer = AutoTokenizer.from_pretrained("google/umt5-xxl")

# Gemma 2 2B, Lumina Image 2.0
gemma2_tokenizer = AutoTokenizer.from_pretrained("unsloth/gemma-2-2b")  # official repo is gated

# LLaMA 3.1 8B, hidream and hunyuan i believe?
llama3_tokenizer = AutoTokenizer.from_pretrained("unsloth/Meta-Llama-3.1-8B-Instruct")  # official repo is gated

# AuraFlow Text encoder (probably pile t5 or something?)
auraflow_tokenizer = AutoTokenizer.from_pretrained("fal/AuraFlow", subfolder="tokenizer")

INCLUDE_TOKENS = False

routes = PromptServer.instance.routes

# not important but, CLIP-G (pretty sure it just has '!' as padding token over L) https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/tree/main/tokenizer_2

# map normalized names → tokenizer instances
tok_map = {
    "clip_l": clip_l_tokenizer,
    "t5": t5_tokenizer,
    "t5_fast": t5_tokenizer_fast,
    "umt5": umt5_tokenizer,
    "gemma2": gemma2_tokenizer,
    "llama3": llama3_tokenizer,
    "auraflow": auraflow_tokenizer,
}


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

    token_counts = {}
    tokens_map = {}

    for name in tok_types:
        key = name.lower().strip()
        tokenizer = tok_map.get(key)
        if tokenizer is None:
            token_counts[name] = None
            if INCLUDE_TOKENS:
                tokens_map[name] = []
            continue

        # run the tokenizer
        outputs = tokenizer(text, return_tensors="pt", add_special_tokens=False)
        num = outputs["input_ids"].shape[1]

        token_counts[name] = num

        if INCLUDE_TOKENS:
            # return the raw token strings too
            # NOTE: unused in JS currently
            ids = outputs["input_ids"][0]
            tokens_map[name] = [tokenizer.convert_ids_to_tokens(int(t)) for t in ids]

    # build response
    resp_data = {"token_counts": token_counts}
    if INCLUDE_TOKENS:
        resp_data["tokens"] = tokens_map

    return web.json_response(resp_data)
