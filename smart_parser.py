import re
import json

def detect_format(lines):
    """Detect dialogue format from sample lines"""
    patterns = {
        'all_caps': r'^[A-Z][A-Z\s]+$',
        'colon': r'^[A-Za-z\s]+:',
        'dash': r'^-\s*[A-Za-z\s]+:',
        'bracket': r'^\[[A-Za-z\s]+\]',
        'parenthesis': r'^\([A-Za-z\s]+\)'
    }
    
    scores = {k: 0 for k in patterns}
    
    for line in lines[:100]:
        stripped = line.strip()
        if not stripped or len(stripped) > 50:
            continue
        for fmt, pattern in patterns.items():
            if re.match(pattern, stripped):
                scores[fmt] += 1
    
    return max(scores, key=scores.get) if max(scores.values()) > 0 else 'all_caps'

def extract_speaker(line, fmt):
    """Extract speaker name based on format"""
    line = line.strip()
    
    if fmt == 'all_caps':
        if re.match(r'^[A-Z][A-Z\s]+$', line):
            return line
    elif fmt == 'colon':
        match = re.match(r'^([A-Za-z\s]+):', line)
        if match:
            return match.group(1).strip()
    elif fmt == 'dash':
        match = re.match(r'^-\s*([A-Za-z\s]+):', line)
        if match:
            return match.group(1).strip()
    elif fmt == 'bracket':
        match = re.match(r'^\[([A-Za-z\s]+)\]', line)
        if match:
            return match.group(1).strip()
    elif fmt == 'parenthesis':
        match = re.match(r'^\(([A-Za-z\s]+)\)', line)
        if match:
            return match.group(1).strip()
    
    return None

def smart_parse(input_file, output_file=None):
    """Parse any dialogue format to JSON"""
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fmt = detect_format(lines)
    print(f"Detected format: {fmt}")
    
    dialogues = []
    current_speaker = None
    current_text = []
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty or metadata
        if not stripped or stripped.startswith('****') or 'Enter' in stripped or 'Exit' in stripped:
            if current_speaker and current_text:
                dialogues.append({"speaker": current_speaker, "text": ' '.join(current_text)})
                current_speaker = None
                current_text = []
            continue
        
        # Stage directions
        if stripped.startswith('(') and stripped.endswith(')'):
            if current_speaker and current_text:
                dialogues.append({"speaker": current_speaker, "text": ' '.join(current_text)})
                current_speaker = None
                current_text = []
            continue
        
        # Try extract speaker
        speaker = extract_speaker(line, fmt)
        if speaker:
            if current_speaker and current_text:
                dialogues.append({"speaker": current_speaker, "text": ' '.join(current_text)})
            current_speaker = speaker
            current_text = []
            # Check if dialogue on same line
            remainder = line.split(':', 1)[-1].strip() if ':' in line else ''
            if remainder and fmt in ['colon', 'dash']:
                current_text.append(remainder)
        elif current_speaker:
            current_text.append(stripped)
    
    if current_speaker and current_text:
        dialogues.append({"speaker": current_speaker, "text": ' '.join(current_text)})
    
    result = {"dialogues": dialogues, "format": fmt}
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    return result

if __name__ == "__main__":
    result = smart_parse("All's Well That Ends Well.txt", "dialogues.json")
    print(f"Parsed {len(result['dialogues'])} dialogues")
