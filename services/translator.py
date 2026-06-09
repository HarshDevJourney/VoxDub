import json
import os

from deep_translator import GoogleTranslator

LANG_MAP = {
    "english": "en",
    "hindi": "hi",
    "spanish": "es",
    "french": "fr",
    "german": "de",
    "italian": "it",
    "portuguese": "pt",
    "russian": "ru",
    "japanese": "ja",
    "korean": "ko",
    "chinese": "zh-CN",
    "arabic": "ar",
    "tamil": "ta",
    "telugu": "te",
    "marathi": "mr",
    "gujarati": "gu",
    "bengali": "bn",
    "punjabi": "pa",
    "urdu": "ur",
    "malayalam": "ml",
    "kannada": "kn"
}

def translate(transcript, source_lang, target_lang):
    translator = GoogleTranslator(
        source=LANG_MAP[source_lang.lower()],
        target=LANG_MAP[target_lang.lower()]
    )
    
    translated_transcript = []

    for seg in transcript:
        translated_transcript.append({
            "speaker": seg["speaker"],
            "start": seg["start"],
            "end": seg["end"],
            "text": translator.translate(seg["text"])
        })

    # Create output folder
    output_folder = "translated_output"
    os.makedirs(output_folder, exist_ok=True)

    # Save JSON
    json_path = os.path.join(
        output_folder,
        f"transcript_{target_lang.lower()}.json"
    )

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(translated_transcript, f, indent=4, ensure_ascii=False)

    return translated_transcript