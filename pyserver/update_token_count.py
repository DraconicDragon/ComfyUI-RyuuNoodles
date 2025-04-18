from aiohttp import web
from server import PromptServer
from transformers import CLIPTokenizer, T5Tokenizer, T5TokenizerFast

# load once at module load

clip_l_tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")  # NOTE: fast version isnt faster
# clip_g_tokenizer = CLIPTokenizer.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", subfolder="tokenizer_2")
t5_tokenizer = T5Tokenizer.from_pretrained("google/t5-v1_1-xxl")
# NOTE: BFL flux dev is also possible, but they should all do the same thing because same speice.model file iirc
t5_tokenizer_fast = T5TokenizerFast.from_pretrained("google/t5-v1_1-xxl")
# todo: consider using google-t5/t5-small?

INCLUDE_TOKENS = False

routes = PromptServer.instance.routes

# not important but, CLIP-G (pretty sure it just has '!' as padding token over L) https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/tree/main/tokenizer_2


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

    # map normalized names → tokenizer instances
    tok_map = {
        "clip_l": clip_l_tokenizer,
        "t5": t5_tokenizer,
        "t5_fast": t5_tokenizer_fast,
        #"llama3": None,
    }

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
        outputs = tokenizer(text, return_tensors="pt")
        num = outputs["input_ids"].shape[1]

        # subtract special tokens
        if key.startswith("clip"):
            num = max(0, num - 2)  # <|startoftext|> and <|endoftext|> tokens
        if key.startswith("t5"):
            num = max(0, num - 1)  # apparently this is a thing? </s> i think?

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
