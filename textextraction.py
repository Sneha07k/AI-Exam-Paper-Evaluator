# textextraction.py
import pytesseract
from PIL import Image
import re
import os

# Optionally configure this externally via environment var or modify path below
DEFAULT_TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.environ.get("TESSERACT_CMD"):
    pytesseract.pytesseract.tesseract_cmd = os.environ.get("TESSERACT_CMD")
else:
    # If windows default exists, set it; otherwise assume tesseract is in PATH
    if os.path.exists(DEFAULT_TESSERACT_CMD):
        pytesseract.pytesseract.tesseract_cmd = DEFAULT_TESSERACT_CMD

def extract_text_from_image(image_path, psm=6, lang="eng"):
    """
    Extract raw text from an image using pytesseract.
    psm: page segmentation mode (6 = assume a single uniform block of text)
    """
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        return ""
    
    try:
        img = Image.open(image_path)
        print(f"Image loaded successfully: {img.size}")
    except Exception as e:
        print(f"Error opening {image_path}: {e}")
        return ""

    try:
        config = f'--psm {psm}'
        raw = pytesseract.image_to_string(img, lang=lang, config=config)
        print(f"OCR extracted {len(raw)} characters")
        return raw
    except Exception as e:
        print(f"OCR error: {e}")
        print("Make sure Tesseract-OCR is installed and path is configured correctly")
        return ""

def clean_text(raw_text):
    """
    Clean and normalize extracted text
    """
    if not raw_text:
        return ""
    
    text = raw_text.replace("\r", "\n")
    # collapse multiple newlines to one
    text = re.sub(r"\n{2,}", "\n", text)
    # remove non-ascii (optional)
    text = re.sub(r"[^\x00-\x7F]+", "", text)
    # trim spaces at ends of lines and remove superfluous spaces
    lines = [ln.strip() for ln in text.splitlines() if ln.strip() != ""]
    cleaned = "\n".join(lines)
    
    print(f"Cleaned text: {len(lines)} lines")
    return cleaned

def split_questions(text):
  
    if not text:
        print("No text to split")
        return []

    lines = text.splitlines()
    q_list = []
    
    print(f"\nParsing {len(lines)} lines for questions...")
    
    for idx, line in enumerate(lines, 1):
        if not line.strip():
            continue
        
        # Try multiple patterns for question identification
        patterns = [
            r'^\s*(Q\s*\.?\s*\d+)[\).\s:-]+(.*)$',  # Q1:, Q.1, Q 1
            r'^\s*(\d+)[\).\s:-]+(.*)$',             # 1., 1), 1:
        ]
        
        matched = False
        for pattern in patterns:
            m = re.match(pattern, line, re.IGNORECASE)
            if m:
                qid_raw = m.group(1).strip()
                ans = m.group(2).strip()
                
                # Normalize QID
                if qid_raw.isdigit():
                    qid = f"Q{qid_raw}"
                else:
                    qid = re.sub(r'\s+', '', qid_raw).upper()
                    if not qid.startswith('Q'):
                        qid = 'Q' + qid
                
                q_list.append((qid, ans))
                print(f"Line {idx}: Matched {qid} -> {ans[:50]}...")
                matched = True
                break
        
        if not matched:
            # Try to split by colon
            if ':' in line:
                parts = line.split(':', 1)
                qid_candidate = parts[0].strip()
                ans = parts[1].strip()
                
                # Check if left side looks like a QID
                if re.match(r'^(Q\.?\s*\d+|\d+)$', qid_candidate, re.IGNORECASE):
                    if qid_candidate.isdigit():
                        qid = f"Q{qid_candidate}"
                    else:
                        qid = re.sub(r'\s+', '', qid_candidate).upper()
                        if not qid.startswith('Q'):
                            qid = 'Q' + qid
                    
                    q_list.append((qid, ans))
                    print(f"Line {idx}: Colon-split {qid} -> {ans[:50]}...")
                    matched = True
        
        if not matched and line.strip():
            # Store unmatched lines for potential sequential assignment
            q_list.append((None, line.strip()))
            print(f"Line {idx}: Unmatched -> {line[:50]}...")

    # Assign sequential IDs to unmatched questions
    final = []
    seq = 1
    max_existing_num = 0
    
    # Find highest Q number already assigned
    for qid, ans in q_list:
        if qid and qid.startswith('Q'):
            try:
                num = int(re.search(r'\d+', qid).group())
                max_existing_num = max(max_existing_num, num)
            except:
                pass
    
    seq = max_existing_num + 1
    
    for qid, ans in q_list:
        if qid is None:
            qid = f"Q{seq}"
            seq += 1
            print(f"Assigned sequential ID: {qid} -> {ans[:50]}...")
        final.append((qid, ans))
    
    print(f"\nTotal questions parsed: {len(final)}")
    return final
