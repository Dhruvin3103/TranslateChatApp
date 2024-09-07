from easygoogletranslate import EasyGoogleTranslate


def translate_mess(mess,src,trg):
    translator = EasyGoogleTranslate(
        source_language=src,
        target_language=trg,
    )
    result = translator.translate(mess)
    print(result) 
    return result

# Output: Dies ist ein Beispiel.