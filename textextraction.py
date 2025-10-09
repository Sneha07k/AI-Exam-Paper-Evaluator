import pytesseract
from PIL import Image
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
image_path = r"C:\Users\sneha\OneDrive\Desktop\AI Exam Paper Evaluator\test_paper.png"

def extract_text(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='eng', config='--psm 6')
        print("Raw OCR Output:\n", text)
        return text
    except Exception as e:
        print(f"Error reading {image_path}: {e}")
        return ""

def clean_text(raw_text):
    text = raw_text.replace("\n\n", "\n")
    text = text.strip()
    text = re.sub(r"[^\x00-\x7F]+", "", text)
    text = re.sub(r"\s+", " ", text)
    print("Cleaned Text:\n", text)
    return text

def split_questions(text):
    q_list = []
    lines = text.split("\n")
    for line in lines:
        if ":" in line:
            parts = line.split(":", 1)
            qid = parts[0].strip()
            ans = parts[1].strip()
            q_list.append((qid, ans))
    return q_list


raw_text = extract_text(image_path)
cleaned_text = clean_text(raw_text)
questions = split_questions(cleaned_text)
print("Extracted Questions:\n", questions)
