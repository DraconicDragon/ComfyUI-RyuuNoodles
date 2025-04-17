from transformers import CLIPTokenizer

# Load the tokenizer from the local directory
tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")

# Your input text
text = "Your input text here"

# Tokenize the text
tokens = tokenizer(text, return_tensors="pt")

# Get the number of tokens
num_tokens = tokens["input_ids"].shape[1]
print(f"Number of tokens: {num_tokens}")

# Decode and print each token
input_ids = tokens["input_ids"][0]
tokens_str = [tokenizer.convert_ids_to_tokens([token_id.item()])[0] for token_id in input_ids]

print("Tokens:")
for i, tok in enumerate(tokens_str):
    print(f"{i}: {tok}")
