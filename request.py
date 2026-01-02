from openai import OpenAI
from embedded import retrieve_context
import json
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from trans import simple_translate
from parse_to_json import parse_to_json
from smart_parser import smart_parse

client = OpenAI(
  base_url="https://integrate.api.nvidia.com/v1",
  api_key="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"
)

def translate_with_context(text_to_translate, target_language="Vietnamese"):
    try:
        context_results = retrieve_context(text_to_translate, top_k=15, window=5)
        simple_trans = simple_translate(text_to_translate, 'vi')
        
        context_parts = []
        for i, (surrounding_dialogues, score, idx) in enumerate(context_results):
            context_parts.append(f"\n--- Context {i+1} ---")
            context_parts.append("\n".join(surrounding_dialogues))
        
        context_str = "\n".join(context_parts)
        reference = f"\n\nReference translation: {simple_trans}" if simple_trans else ""
        
        messages = [
            {"content": f"""You are an expert literary translator specializing in classical drama and RPG games.

Key principles:
- Preserve the emotional tone and dramatic weight of the original
- Maintain character voice and formality level
- Keep metaphors and imagery culturally appropriate
- Use natural {target_language} that sounds authentic, not mechanical

Here are similar dialogues with their surrounding context for reference:
{context_str}{reference}""", 'role': 'system'},
            {"content": f"Translate this dialogue to {target_language}, preserving its dramatic and emotional essence:\n\n{text_to_translate}\n\nProvide ONLY the translation, no explanations.", 'role': 'user'}
        ]
        
        completion = client.chat.completions.create(
            model="deepseek-ai/deepseek-v3.1-terminus",
            messages=messages,
            temperature=0.3,
            top_p=0.9,
            max_tokens=4096,
        )
        
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error translating: {e}")
        return text_to_translate

def translate_file(input_file, output_file, target_language="Vietnamese", rpm=30, max_workers=5):
    # Parse to JSON with smart detection
    data = smart_parse(input_file)
    dialogues = data['dialogues']
    
    translations = {}
    delay = 60.0 / rpm
    lock = threading.Lock()
    last_request_time = [time.time()]
    
    def translate_with_rate_limit(dialogue):
        with lock:
            elapsed = time.time() - last_request_time[0]
            if elapsed < delay:
                time.sleep(delay - elapsed)
            last_request_time[0] = time.time()
        
        text = dialogue['text']
        translation = translate_with_context(text, target_language)
        return text, translation
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(translate_with_rate_limit, d): d for d in dialogues}
        
        for future in tqdm(as_completed(futures), total=len(dialogues), desc="Translating", unit="dialogue"):
            text, translation = future.result()
            translations[text] = translation
    
    # Replace in original file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = content
    for original, translation in translations.items():
        if translation:
            result = result.replace(original, translation, 1)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f"\nTranslation complete! Saved to {output_file}")
    print(f"Translated {len(translations)} dialogues")

if __name__ == "__main__":
    translate_file("All's Well That Ends Well.txt", "All's Well That Ends Well_Vietnamese.txt", "Vietnamese", rpm=40, max_workers=10)

