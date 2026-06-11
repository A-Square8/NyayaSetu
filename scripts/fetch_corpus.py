import os
import shutil

def fetch_pdfs():
    source_dir = "Data"
    dest_dir = "data/docs"
    
    os.makedirs(dest_dir, exist_ok=True)
    
    for filename in os.listdir(source_dir):
        if filename.endswith(".pdf"):
            src_path = os.path.join(source_dir, filename)
            dst_path = os.path.join(dest_dir, filename)
            shutil.copy2(src_path, dst_path)

if __name__ == "__main__":
    fetch_pdfs()
