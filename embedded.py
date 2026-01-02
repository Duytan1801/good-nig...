from openai import OpenAI
from vector_store import VectorStore
import re

client = OpenAI(
  api_key="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",
  base_url="https://integrate.api.nvidia.com/v1"
)

def parse_dialogues(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by character names (all caps words at start of line)
    pattern = r'^([A-Z][A-Z\s]+)$'
    lines = content.split('\n')
    
    dialogues = []
    current_speaker = None
    current_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Skip stage directions and scene markers
        if not stripped or stripped.startswith('****') or 'Enter' in stripped or 'Exit' in stripped or stripped.startswith('('):
            continue
        
        # Check if it's a speaker name (all uppercase)
        if re.match(pattern, stripped):
            # Save previous dialogue
            if current_speaker and current_lines:
                full_text = ' '.join(current_lines)
                dialogues.append((current_speaker, full_text))
            
            current_speaker = stripped
            current_lines = []
        elif current_speaker:
            current_lines.append(stripped)
    
    # Add last dialogue
    if current_speaker and current_lines:
        full_text = ' '.join(current_lines)
        dialogues.append((current_speaker, full_text))
    
    return dialogues

def embed_dialogues(dialogues, batch_size=10):
    store = VectorStore()
    
    texts = [f"{speaker}: {text}" for speaker, text in dialogues]
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        response = client.embeddings.create(
            input=batch,
            model="nvidia/llama-3.2-nemoretriever-300m-embed-v2",
            encoding_format="float",
            extra_body={"input_type": "passage", "truncate": "NONE"}
        )
        
        for j, data in enumerate(response.data):
            store.add(batch[j], data.embedding)
        
        print(f"Embedded {min(i+batch_size, len(texts))}/{len(texts)} dialogues")
    
    store.save()
    print("Embeddings saved!")
    return store

def retrieve_context(query, top_k=3, window=2):
    store = VectorStore()
    if not store.load():
        print("No embeddings found. Run embed_dialogues first.")
        return []
    
    response = client.embeddings.create(
        input=[query],
        model="nvidia/llama-3.2-nemoretriever-300m-embed-v2",
        encoding_format="float",
        extra_body={"input_type": "query", "truncate": "NONE"}
    )
    
    query_embedding = response.data[0].embedding
    results = store.search_with_surrounding(query_embedding, top_k, window)
    return results

if __name__ == "__main__":
    dialogues = parse_dialogues("All's Well That Ends Well.txt")
    print(f"Found {len(dialogues)} dialogues")
    embed_dialogues(dialogues)
