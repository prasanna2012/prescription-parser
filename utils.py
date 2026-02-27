from PIL import Image
import pytesseract
from deep_translator import GoogleTranslator
import pyttsx3
from io import BytesIO

# ---------------- TESSERACT PATH ----------------
# Make sure this is the correct path on your system
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------------- OCR FUNCTION ----------------
def extract_text(image: Image.Image) -> str:
    """
    Extract text from an image using Tesseract OCR.
    
    Args:
        image (PIL.Image.Image): Prescription image

    Returns:
        str: Extracted text
    """
    try:
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""

# ---------------- TRANSLATION / SIMPLIFICATION ----------------
def simplify_text(text: str, target_lang: str = "en") -> str:
    """
    Translate text to a target language using GoogleTranslator.
    
    Args:
        text (str): Original text
        target_lang (str): Language code (e.g., 'en', 'hi', 'te')

    Returns:
        str: Translated/simplified text
    """
    if not text:
        return ""
    try:
        simplified = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return simplified
    except Exception as e:
        print(f"Translation Error: {e}")
        return text  # Return original text if translation fails

# ---------------- TEXT-TO-SPEECH ----------------
def text_to_speech(text: str) -> BytesIO:
    """
    Convert text to speech using pyttsx3 and return as BytesIO object for Streamlit audio.
    
    Args:
        text (str): Text to convert to audio

    Returns:
        BytesIO: Audio stream
    """
    audio_stream = BytesIO()
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)   # Speech rate
        engine.setProperty('volume', 1.0) # Volume (0.0 to 1.0)

        # Save audio to temporary file
        temp_file = "output_audio.mp3"
        engine.save_to_file(text, temp_file)
        engine.runAndWait()

        # Load audio into BytesIO
        with open(temp_file, "rb") as f:
            audio_stream.write(f.read())
        audio_stream.seek(0)

    except Exception as e:
        print(f"TTS Error: {e}")
    
    return audio_stream