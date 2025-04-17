from aiohttp import web
from server import PromptServer
from transformers import CLIPTokenizer

# load once at module load
tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")
routes = PromptServer.instance.routes


@routes.post("/ryuu/update_token_count")
async def update_token_count(request):
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    text = data.get("text", "")
    if not text:
        return web.json_response({"error": "No text provided"}, status=400)
    print(text)
    tokens = tokenizer(text, return_tensors="pt")
    num_tokens = tokens["input_ids"].shape[1]
    num_tokens = num_tokens - 2 # Doing minus 2 because start/end tokens are not included 
    input_ids = tokens["input_ids"][0]
    tokens_str = [tokenizer.convert_ids_to_tokens(int(t)) for t in input_ids]

    return web.json_response({"token_count": num_tokens, "tokens": tokens_str})
