import csv
def load_answer_key(file_path="answer_keys.csv"):
    key = {}
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            if len(row) >= 5:
                qid = row[0].strip()
                answer = row[2].strip()
                marks = float(row[3].strip())
                qtype = row[4].strip()[0].upper()  
                key[qid] = {"answer": answer, "marks": marks, "type": qtype}
    return key


def evaluate_objective(student_ans, correct_ans, marks):
    if student_ans.lower().strip() == correct_ans.lower().strip():
        return marks, "Correct"
    else:
        return 0, f"Incorrect (Expected: {correct_ans})"


def evaluate_subjective(student_ans, correct_ans, marks):
    keywords = correct_ans.lower().split()
    student_words = student_ans.lower().split()
    score = 0
    for kw in keywords:
        if kw in student_words:
            score += marks / len(keywords)
    if score == marks:
        remark = "Excellent"
    elif score > 0:
        remark = "Partial"
    else:
        remark = f"Incorrect (Expected keywords: {correct_ans})"
    return round(score, 2), remark





    
answer_key = {
"Q1": {"answer": "Paris", "marks": 2, "type": "O"},
"Q2": {"answer": "Machine Learning is a subset of AI", "marks": 5, "type": "S"}
    }

student_answers = {
"Q1": "paris",
"Q2": "AI includes Machine Learning and Deep Learning"
}

    
for qid, data in answer_key.items():
    correct = data["answer"]
    marks = data["marks"]
    qtype = data["type"]
    student = student_answers.get(qid, "")

    if qtype == "O":
        score, remark = evaluate_objective(student, correct, marks)
    else:
        score, remark = evaluate_subjective(student, correct, marks)

    print(f"{qid}: {student}")
    print(f"→ Score: {score}/{marks} | Remark: {remark}\n")
