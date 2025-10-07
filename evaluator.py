
import re


def clean_text(text):
    
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return set(text.split())


def evaluate_objective(student_obj, correct_obj):
    
    score = 0
    for q, ans in student_obj.items():
        if q in correct_obj and ans.strip().upper() == correct_obj[q].strip().upper():
            score += 1
    return score


def compare_subjective(student_answer, correct_answer):
   
    s_words = clean_text(student_answer)
    c_words = clean_text(correct_answer)
    if not s_words or not c_words:
        return 0
    common = s_words.intersection(c_words)
    return (len(common) / len(c_words)) * 100


def evaluate_all_subjective(student_ans, correct_ans, weights):
   
    total = 0
    for q, correct in correct_ans.items():
        student_response = student_ans.get(q, "")
        if not student_response:
            continue
        similarity = compare_subjective(student_response, correct)
        mark = (similarity / 100) * weights.get(q, 5)
        total += round(mark, 2)
    return round(total, 2)


def calculate_total_score(obj_score, subj_score):
    
    return round(obj_score + subj_score, 2)
