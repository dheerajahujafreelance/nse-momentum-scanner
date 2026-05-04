import os
import shutil
from datetime import datetime

def clean_folder(folder_path):
    """Delete all contents of a folder but keep the folder itself"""
    if os.path.exists(folder_path):
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
                print(f"   Deleted file: {item_path}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"   Deleted folder: {item_path}")
        print(f"✅ Cleaned: {folder_path}")
    else:
        os.makedirs(folder_path, exist_ok=True)
        print(f"✅ Created: {folder_path}")

def main():
    print("\n" + "="*50)
    print("CLEANING DATA FOLDERS")
    print("="*50)
    
    # Define folders to clean
    folders_to_clean = [
        'data/raw',
        'data/filtered',
        'data/reference',
        'output'
    ]
    
    for folder in folders_to_clean:
        print(f"\n📁 Processing: {folder}")
        clean_folder(folder)
    
    print("\n" + "="*50)
    print("✅ CLEANUP COMPLETE")
    print("="*50)

if __name__ == "__main__":
    main()
