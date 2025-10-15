# results.py
import pandas as pd
import os
from datetime import datetime
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ANSWER_KEYS_DIR = os.path.join(DATA_DIR, "answer_keys")
RESULTS_FILE = os.path.join(DATA_DIR, "results.csv")

os.makedirs(ANSWER_KEYS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

def save_results(student_name, username, total_score, detailed_results, answer_key_name):
    """
    - append summary to results.csv with columns:
      Student, EvaluatorUser, AnswerKey, Total Score, Timestamp
    - save detailed per-student file Student_timestamp_details.csv
    """

    # ✅ FIX: Use Windows-safe timestamp (no colons)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    summary = {
        "Student": student_name,
        "EvaluatorUser": username,
        "AnswerKey": answer_key_name,
        "Total Score": total_score,
        "Timestamp": timestamp
    }

    # write or append summary
    if os.path.exists(RESULTS_FILE):
        df = pd.read_csv(RESULTS_FILE)
        df = pd.concat([df, pd.DataFrame([summary])], ignore_index=True)
        df.to_csv(RESULTS_FILE, index=False)
    else:
        df = pd.DataFrame([summary])
        df.to_csv(RESULTS_FILE, index=False)

    # safe file naming
    safe_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in student_name)

    details_file = os.path.join(DATA_DIR, f"{safe_name}_{timestamp}_details.csv")
    detailed_df = pd.DataFrame.from_dict(detailed_results, orient='index')
    detailed_df.index.name = "QID"
    detailed_df.to_csv(details_file)

    return summary, details_file

def list_answer_keys():
    files = sorted(os.listdir(ANSWER_KEYS_DIR))
    return [f for f in files if f.lower().endswith(".csv")]

def class_analysis(result_file=RESULTS_FILE):
    if not os.path.exists(result_file):
        print("No results yet.")
        return None
    df = pd.read_csv(result_file)
    total_students = len(df)
    average_score = df["Total Score"].mean()
    max_score = df["Total Score"].max()
    min_score = df["Total Score"].min()
    # pass criterion: >= 33% of maximum observed score in file
    pass_mark_threshold = max_score * 0.33 if max_score and not pd.isna(max_score) else 0
    passed = len(df[df["Total Score"] >= pass_mark_threshold])
    failed = total_students - passed
    analysis = {
        "Total Students": int(total_students),
        "Average Score": float(round(average_score, 2)) if total_students else 0.0,
        "Highest Score": float(max_score) if not pd.isna(max_score) else 0.0,
        "Lowest Score": float(min_score) if not pd.isna(min_score) else 0.0,
        "Passed": int(passed),
        "Failed": int(failed),
        "PassThreshold": pass_mark_threshold
    }
    return analysis
