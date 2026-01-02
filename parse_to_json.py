import json
import re

def parse_to_json(input_file, output_file=None):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    dialogues = []
    current_speaker = None
    current_text = []
    metadata = []
    
    for line in lines:
        stripped = line.strip()
        
        # Capture metadata (scene markers, stage directions)
        if not stripped or stripped.startswith('****') or 'Enter' in stripped or 'Exit' in stripped:
            if current_speaker and current_text:
                dialogues.append({
                    "speaker": current_speaker,
                    "text": ' '.join(current_text)
                })
                current_speaker = None
                current_text = []
            if stripped:
                metadata.append({"type": "stage", "content": stripped})
            continue
        
        # Stage directions in parentheses
        if stripped.startswith('(') and stripped.endswith(')'):
            if current_speaker and current_text:
                dialogues.append({
                    "speaker": current_speaker,
                    "text": ' '.join(current_text),
                    "direction": stripped
                })
                current_speaker = None
                current_text = []
            else:
                metadata.append({"type": "direction", "content": stripped})
            continue
        
        # Speaker name (all caps or ends with colon)
        if re.match(r'^[A-Z][A-Z\s]+$', stripped) or (stripped.endswith(':') and len(stripped.split()) <= 3):
            if current_speaker and current_text:
                dialogues.append({
                    "speaker": current_speaker,
                    "text": ' '.join(current_text)
                })
            current_speaker = stripped.rstrip(':')
            current_text = []
        elif current_speaker:
            current_text.append(stripped)
    
    if current_speaker and current_text:
        dialogues.append({
            "speaker": current_speaker,
            "text": ' '.join(current_text)
        })
    
    result = {"dialogues": dialogues, "metadata": metadata}
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    return result

if __name__ == "__main__":
    parse_to_json("All's Well That Ends Well.txt", "dialogues.json")
    print("Parsed to JSON successfully!")
