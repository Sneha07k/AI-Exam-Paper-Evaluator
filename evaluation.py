# evaluation.py
import csv
import os
import re

def load_answer_key(file_path):
    """
    Expect CSV with header: QID,Question,Answer,Marks,Type
    Type: O or S (Objective or Subjective)
    """
    key = {}
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Answer key file not found: {file_path}")
    
    try:
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                qid = row["QID"].strip()

                # Normalize QID format
                if qid.isdigit():
                    qid = f"Q{qid}"
                elif not qid.upper().startswith("Q"):
                    qid = "Q" + qid

                qid = qid.upper()

                if not qid:
                    continue
                
                answer = (row.get("Answer") or "").strip()
                marks_raw = row.get("Marks") or row.get("Score") or "1"
                try:
                    marks = float(marks_raw)
                except:
                    marks = 1.0
                
                qtype = (row.get("Type") or "S").strip().upper()
                # Map common type variations
                if qtype.startswith("O"):
                    qtype = "O"
                elif qtype.startswith("S"):
                    qtype = "S"
                else:
                    qtype = "S"  # Default to subjective
                
                key[qid] = {"answer": answer, "marks": marks, "type": qtype}
        
        print(f"Loaded {len(key)} questions from answer key")
        return key
    except Exception as e:
        print(f"Error loading answer key: {e}")
        raise

def evaluate_objective(student_ans, correct_ans, marks):
    """
    Exact match comparison for objective questions
    """
    if student_ans is None:
        student_ans = ""
    
    # Normalize both answers for comparison
    student_normalized = student_ans.strip().lower()
    correct_normalized = correct_ans.strip().lower()
    
    if student_normalized == correct_normalized:
        return marks, "Correct"
    else:
        return 0.0, f"Incorrect (Expected: {correct_ans})"

def evaluate_subjective(student_ans, correct_ans, marks):
    """
    Keyword-based matching for subjective questions.
    Awards proportional marks based on keyword presence.
    """
    if student_ans is None or student_ans.strip() == "":
        return 0.0, "No answer provided"
    
    keywords = [k for k in re_split_keywords(correct_ans) if k and len(k) > 2]
    
    if not keywords:
        # If no valid keywords, give full marks if student wrote something
        if len(student_ans.strip()) > 5:
            return marks, "Answer provided (no keywords to match)"
        return 0.0, "No answer or keywords"
    
    student_lower = student_ans.lower()
    matched_keywords = []
    
    for kw in keywords:
        if kw.lower() in student_lower:
            matched_keywords.append(kw)
    
    # Calculate score based on matched keywords
    score = (len(matched_keywords) / len(keywords)) * marks
    score = round(score, 2)
    
    # Generate remark
    if score == marks:
        remark = "Excellent - All keywords present"
    elif score >= marks * 0.7:
        remark = f"Good - Matched {len(matched_keywords)}/{len(keywords)} keywords"
    elif score > 0:
        remark = f"Partial - Matched {len(matched_keywords)}/{len(keywords)} keywords"
    else:
        remark = f"Insufficient - Expected keywords: {', '.join(keywords[:5])}"
    
    return score, remark

def re_split_keywords(text):
    """
    Split text into meaningful keywords
    """
    # Split by common delimiters and filter out short/common words
    tokens = re.split(r'[\s,;:.()!?\-]+', text)
    # Filter out very short words and common stop words
    stop_words = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'of'}
    keywords = [t.strip() for t in tokens if t.strip() and len(t.strip()) > 2 and t.lower() not in stop_words]
    return keywords

def evaluate_all(student_answers, answer_key):
    """
    Evaluate all questions and return detailed results.
    
    Args:
        student_answers: dict QID -> answer text
        answer_key: dict QID -> {answer, marks, type}
    
    Returns:
        detailed_results: dict with per-question results
        total_score: float total score achieved
    """
    detailed = {}
    total_score = 0.0
    
    print(f"\nEvaluating {len(answer_key)} questions...")
    print(f"Student provided answers for {len(student_answers)} questions")
    
    for qid, keydata in answer_key.items():
        correct = keydata.get("answer", "")
        marks = keydata.get("marks", 1.0)
        qtype = keydata.get("type", "S")
        
        student_ans = student_answers.get(qid, "")
        
        print(f"\n{qid}: Type={qtype}, Marks={marks}")
        print(f"  Expected: {correct}")
        print(f"  Student:  {student_ans}")
        
        if qtype == "O":
            score, remark = evaluate_objective(student_ans, correct, marks)
        else:
            score, remark = evaluate_subjective(student_ans, correct, marks)
        
        print(f"  Result: {score}/{marks} - {remark}")
        
        detailed[qid] = {
            "StudentAnswer": student_ans,
            "Score": float(score),
            "Marks": float(marks),
            "Remark": remark,
            "CorrectAnswer": correct,
            "Type": qtype
        }
        total_score += float(score)
    
    return detailed, round(total_score, 2)
