#!/usr/bin/env python3
import os
from request import translate_file
from embedded import parse_dialogues, embed_dialogues

def main():
    print("=" * 50)
    print("Context-Aware Translator")
    print("=" * 50)
    
    # Input file
    input_path = input("\nEnter input file path: ").strip()
    if not os.path.exists(input_path):
        print("Error: File not found!")
        return
    
    # Output file
    default_output = input_path.rsplit('.', 1)[0] + "_translated.txt"
    output_path = input(f"Enter output file path (default: {default_output}): ").strip()
    if not output_path:
        output_path = default_output
    
    # Target language
    print("\nAvailable languages:")
    print("1. Vietnamese (vi)")
    print("2. Spanish (es)")
    print("3. French (fr)")
    print("4. German (de)")
    print("5. Japanese (ja)")
    print("6. Chinese (zh)")
    print("7. Other")
    
    choice = input("Select language (1-7): ").strip()
    lang_map = {"1": "Vietnamese", "2": "Spanish", "3": "French", 
                "4": "German", "5": "Japanese", "6": "Chinese"}
    
    if choice == "7":
        target_lang = input("Enter language name: ").strip()
    else:
        target_lang = lang_map.get(choice, "Vietnamese")
    
    # Vectorize input file
    print("\nVectorizing input file...")
    dialogues = parse_dialogues(input_path)
    print(f"Found {len(dialogues)} dialogues")
    embed_dialogues(dialogues)
    
    # Translate
    print(f"\nTranslating to {target_lang}...")
    translate_file(input_path, output_path, target_lang, rpm=40, max_workers=10)
    
    print(f"\n✓ Done! Output saved to: {output_path}")

if __name__ == "__main__":
    main()
