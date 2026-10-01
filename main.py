import os
from collections import defaultdict
from PIL import Image
import imagehash

# Configuration
IMAGE_FOLDER = "/mnt/D/Ei"  # Change this to your folder path
HASH_SIZE = 8  # 8 means an 8x8 hash (64 bits). Good balance of speed and accuracy.

def find_duplicates(folder_path):
    # Dictionary to group matching hashes: { 'hash_string': ['path1', 'path2'] }
    hash_map = defaultdict(list)
    corrupted_files = []
    
    print("Scanning images and calculating hashes...")
    
    # Supported image extensions
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
    
    # 1. Loop through all files once - O(N)
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(valid_extensions):
                file_path = os.path.join(root, file)
                
                try:
                    with Image.open(file_path) as img:
                        # phash = Perceptual Hash (resilient to resizing/compression)
                        img_hash = imagehash.phash(img, hash_size=HASH_SIZE)
                        
                        # Convert hash to string to use as a dictionary key
                        hash_str = str(img_hash)
                        if hash_map[hash_str] and len(hash_map[hash_str]) > 0:
                            org_file_name = hash_map[hash_str][0]

                            day_sub_end= org_file_name.find("_")
                            day_sub_end_cur = file_path.find("_")
                            if not (day_sub_end and day_sub_end_cur):
                                hash_map[hash_str].append(file_path)
                                continue

                            day_index = org_file_name[0:day_sub_end]
                            day_index_cur = file_path[0:day_sub_end_cur]
                            if day_index == day_index_cur:
                                print(f"{day_index} {day_index_cur}")
                                      
                                continue
                            
                            hash_map[hash_str].append(file_path)
                        else:
                            hash_map[hash_str].append(file_path)

                except Exception as e:
                    corrupted_files.append((file_path, str(e)))

    # 2. Extract duplicates
    duplicates = {img_hash: paths for img_hash, paths in hash_map.items() if len(paths) > 1}
    
    return duplicates, corrupted_files

if __name__ == "__main__":
    duplicates, corrupted = find_duplicates(IMAGE_FOLDER)
    
    print("\n=== RESULTS ===")
    if not duplicates:
        print("No duplicates found!")
    else:
        print(f"Found {len(duplicates)} groups of duplicate images:\n")
        for i, (img_hash, paths) in enumerate(duplicates.items(), 1):
            print(f"Group {i} (Hash: {img_hash}):")
            for path in paths:
                print(f"  - {path}")
            print("-" * 40)
            
    if corrupted:
        print(f"\n[Warning] Skipped {len(corrupted)} unreadable/corrupted files.")
