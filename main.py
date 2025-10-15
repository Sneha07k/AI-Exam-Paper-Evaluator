# main.py
import os
import sys
import re
from textextraction import extract_text_from_image, clean_text, split_questions
from evaluation import load_answer_key, evaluate_all
from results import save_results, list_answer_keys, class_analysis
from utils import ensure_dirs, copy_answer_key_to_store

def pause():
    input("\nPress Enter to continue...")

def choose_answer_key():
    """
    Let user choose from available answer keys
    """
    keys = list_answer_keys()
    if not keys:
        print("\n❌ No answer keys uploaded yet.")
        print("Please upload an answer key first (Option 1 from main menu)")
        return None
    
    print("\n📋 Available answer keys:")
    for i, k in enumerate(keys, 1):
        print(f"  {i}. {k}")
    
    choice = input("\nChoose by number (or 0 to cancel): ").strip()
    try:
        if choice == "0":
            return None
        idx = int(choice) - 1
        if idx < 0 or idx >= len(keys):
            print("Invalid choice.")
            return None
        
        answer_key_path = os.path.join(os.path.dirname(__file__), "data", "answer_keys", keys[idx])
        return answer_key_path, keys[idx]
    except ValueError:
        print("Invalid input. Please enter a number.")
        return None

def upload_answer_key_flow():
    """
    Upload a new answer key CSV file
    """
    print("\n📤 Upload Answer Key")
    print("=" * 50)
    path = input("Enter full path to answer key CSV file: ").strip()
    
    # Remove quotes if user copied path with quotes
    path = path.strip('"').strip("'")
    
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        return
    
    if not path.lower().endswith('.csv'):
        print("❌ File must be a CSV file")
        return
    
    try:
        dest_path, dest_name = copy_answer_key_to_store(path)
        print(f"✅ Successfully uploaded answer key!")
        print(f"   Saved as: data/answer_keys/{dest_name}")
    except Exception as e:
        print(f"❌ Error uploading answer key: {e}")

def grade_flow(username):
    """
    Grade a scanned student answer sheet
    """
    print("\n📝 Grade Student Answer Sheet")
    print("=" * 50)
    
    # Choose answer key
    ak = choose_answer_key()
    if not ak:
        print("❌ No answer key selected. Returning to menu.")
        return
    
    path, keyname = ak
    print(f"✅ Using answer key: {keyname}")
    
    # Get image path
    image_path = input("\nEnter path to student's scanned image (PNG/JPG): ").strip()
    image_path = image_path.strip('"').strip("'")
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    # Get student name
    student_name = input("Enter student name (for record): ").strip()
    if not student_name:
        student_name = "Unknown"
    
    print("\n🔍 Running OCR on image...")
    print("-" * 50)
    
    # Extract text
    raw = extract_text_from_image(image_path)
    if not raw or len(raw.strip()) < 10:
        print("⚠️  Warning: Very little text extracted from image.")
        print("   This might be due to:")
        print("   - Poor image quality")
        print("   - Incorrect Tesseract installation/path")
        print("   - Unsupported image format")
        cont = input("\nContinue anyway? (y/n): ").strip().lower()
        if cont != 'y':
            return
    
    # Clean and parse
    cleaned = clean_text(raw)
    q_pairs = split_questions(cleaned)
    
    if not q_pairs:
        print("❌ No questions detected in the image!")
        print("   Please check:")
        print("   - Image quality and readability")
        print("   - Question format (should be like Q1:, 1., etc.)")
        return
    
    # Convert list to dict QID->answer
    student_answers = {qid: ans for qid, ans in q_pairs}
    
    print(f"\n✅ Detected {len(student_answers)} questions from student sheet")
    
    # Load key and evaluate
    try:
        answer_key = load_answer_key(path)
    except Exception as e:
        print(f"❌ Error loading answer key: {e}")
        return
    
    print(f"✅ Loaded {len(answer_key)} questions from answer key")
    
    # Check for mismatches
    key_qids = set(answer_key.keys())
    student_qids = set(student_answers.keys())
    
    if key_qids != student_qids:
        print("\n⚠️  Warning: Question ID mismatch detected!")
        only_in_key = key_qids - student_qids
        only_in_student = student_qids - key_qids
        
        if only_in_key:
            print(f"   Questions in key but not in student sheet: {sorted(only_in_key)}")
        if only_in_student:
            print(f"   Questions in student sheet but not in key: {sorted(only_in_student)}")
        
        cont = input("\nContinue with evaluation? (y/n): ").strip().lower()
        if cont != 'y':
            return
    
    # Evaluate
    print("\n🔄 Evaluating answers...")
    print("=" * 50)
    
    detailed, total_score = evaluate_all(student_answers, answer_key)
    
    # Display results
    print(f"\n📊 Results for: {student_name}")
    print("=" * 50)
    
    for qid in sorted(detailed.keys(), key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0):
        info = detailed[qid]
        print(f"\n{qid} [{info['Type']}]:")
        print(f"  Score: {info['Score']}/{info['Marks']}")
        print(f"  Remark: {info['Remark']}")
        if len(info['StudentAnswer']) > 100:
            print(f"  Student: {info['StudentAnswer'][:100]}...")
        else:
            print(f"  Student: {info['StudentAnswer']}")
    
    print("\n" + "=" * 50)
    print(f"🎯 TOTAL SCORE: {total_score}")
    print("=" * 50)
    
    # Save results
    try:
        summary, details_file = save_results(student_name, username, total_score, detailed, keyname)
        print(f"\n✅ Results saved successfully!")
        print(f"   Summary: data/results.csv")
        print(f"   Details: {os.path.basename(details_file)}")
    except Exception as e:
        print(f"❌ Error saving results: {e}")

def analytics_flow():
    """
    Show class performance analytics
    """
    print("\n📈 Class Performance Analytics")
    print("=" * 50)
    
    analysis = class_analysis()
    if not analysis:
        return
    
    print(f"\nTotal Students:    {analysis['Total Students']}")
    print(f"Average Score:     {analysis['Average Score']:.2f}")
    print(f"Highest Score:     {analysis['Highest Score']:.2f}")
    print(f"Lowest Score:      {analysis['Lowest Score']:.2f}")
    print(f"Pass Threshold:    {analysis['PassThreshold']:.2f} (33% of max)")
    print(f"Passed:            {analysis['Passed']} students")
    print(f"Failed:            {analysis['Failed']} students")
    
    if analysis['Total Students'] > 0:
        pass_rate = (analysis['Passed'] / analysis['Total Students']) * 100
        print(f"Pass Rate:         {pass_rate:.1f}%")

def main():
    ensure_dirs()
    
    print("=" * 60)
    print("    🎓 EXAM PAPER EVALUATOR SYSTEM 🎓")
    print("=" * 60)
    
    user = None
   
    while True:
       
        print("  📋 Main Menu:")
        print("    1) Upload a new answer key CSV")
        print("    2) List answer keys")
        print("    3) Grade a scanned answer sheet")
        print("    4) View class analytics")
        print("    5) Logout / Exit")
        print("=" * 60)
        
        choice = input("\nChoose option: ").strip()
        
        if choice == "1":
            upload_answer_key_flow()
            pause()
        elif choice == "2":
            keys = list_answer_keys()
            if not keys:
                print("\n📋 No answer keys uploaded yet.")
            else:
                print("\n📋 Available Answer Keys:")
                for i, k in enumerate(keys, 1):
                    print(f"  {i}. {k}")
            pause()
        elif choice == "3":
            grade_flow(user)
            pause()
        elif choice == "4":
            analytics_flow()
            pause()
        elif choice == "5":
            print("\n👋 Logging out. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please choose 1-5.")

if __name__ == "__main__":
    main()