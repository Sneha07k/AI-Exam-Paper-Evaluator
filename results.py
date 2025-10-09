import pandas as pd

def save_results(student_name, total_score, detailed_results, result_file="results.csv"):
   
    summary_df = pd.DataFrame([{"Student": student_name, "Total Score": total_score}])

    try:
        existing_df = pd.read_csv(result_file)
        summary_df.to_csv(result_file, mode='a', header=False, index=False)
    except FileNotFoundError:
        summary_df.to_csv(result_file, index=False)

   
    details_file = f"{student_name}_details.csv"
    detailed_df = pd.DataFrame(detailed_results).T
    detailed_df.to_csv(details_file, index_label="QID")
    print(f"Saved results for {student_name} ")


def class_analysis(result_file="results.csv"):
    
    try:
        df = pd.read_csv(result_file)
    except FileNotFoundError:
        print("No results found.")
        return

    total_students = len(df)
    average_score = df["Total Score"].mean()
    max_score = df["Total Score"].max()
    min_score = df["Total Score"].min()
    passed = len(df[df["Total Score"] >= df["Total Score"].max() * 0.33])
    failed = total_students - passed

    print("\n Class Analysis:")
    print(f"Total Students: {total_students}")
    print(f"Average Score: {average_score:.2f}")
    print(f"Highest Score: {max_score}")
    print(f"Lowest Score: {min_score}")
    print(f"Passed: {passed}, Failed: {failed}")



sample_results = {
    "Q1": {"Answer": "Paris", "Score": 1},
    "Q2": {"Answer": "4", "Score": 1},
    "Q3": {"Answer": "Albert Einstein", "Score": 2},
    "Q4": {"Answer": "Simulation of human intelligence", "Score": 2},
    "Q5": {"Answer": "Jupiter", "Score": 1},
    }

    
save_results("Sneha", total_score=7, detailed_results=sample_results)

   
class_analysis()
