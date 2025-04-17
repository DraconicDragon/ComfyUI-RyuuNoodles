from aiohttp import web
from server import PromptServer
from transformers import CLIPTokenizer, T5Tokenizer, T5TokenizerFast

# load once at module load

clip_l_tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")  # NOTE: fast version isnt faster
# clip_g_tokenizer = CLIPTokenizer.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", subfolder="tokenizer_2")
t5_tokenizer = T5Tokenizer.from_pretrained("google/t5-v1_1-xxl")
# NOTE: BFL flux dev is also possible, but they should all do the same thing because same speice.model file iirc
t5_tokenizer_fast = T5TokenizerFast.from_pretrained("google/t5-v1_1-xxl")

routes = PromptServer.instance.routes

# todo: add support for T5 etc. tokenizers
# not important but, CLIP-G (pretty sure it just has '!' as padding token over L) https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/tree/main/tokenizer_2


@routes.post("/ryuu/update_token_count")
async def update_token_count(request):
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    text = data.get("text", "")
    if not text:
        return web.json_response({"error": "No text provided"}, status=400)

    tokenizer = clip_l_tokenizer

    tokens = tokenizer(text, return_tensors="pt")
    num_tokens = tokens["input_ids"].shape[1]
    num_tokens = num_tokens - 2  # Doing minus 2 because start/end tokens are not included *CLIP only*
    # todo: t5 doesnt have this, technically only </s> at the end but you can tell it to not include that? would be 511 usable tokens in the end per chunk
    # todo: see if hidden inputs are still supported by latest comfy frontend and use button on node to switch tokenizer mode and the hidden input to save the tokenizer mode
    input_ids = tokens["input_ids"][0]
    tokens_str = [tokenizer.convert_ids_to_tokens(int(t)) for t in input_ids]

    return web.json_response({"token_count": num_tokens, "tokens": tokens_str})
