from translate import Translator

def simple_translate(text, to_lang='vi'):
    try:
        translator = Translator(to_lang=to_lang, provider='mymemory')
        return translator.translate(text)
    except:
        return None