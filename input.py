import os

def load_exam_papers(folder_path: str) -> list:
    papers = []
    for name in os.listdir(folder_path):
        if name.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.txt')):
            papers.append(folder_path + '/' + name)
    return papers
