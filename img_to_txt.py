import os
try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None


def extract_text_from_image(file_path):
   
    if not os.path.exists(file_path):
        print("❌ File not found.")
        return ""

    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    if pytesseract:
        try:
            return pytesseract.image_to_string(Image.open(file_path))
        except Exception as e:
            print(f"❌ OCR failed: {e}")
            return ""
    else:
        print("OCR not available")
        return ""
