import os
import openpyxl
import re

def normalize(s):
    if not s:
        return ""
    # remove extensions, non-alphanumeric, spaces, lowercase
    s = s.split('.')[0]
    s = re.sub(r'[^a-zA-Z0-9]', '', s).lower()
    return s

def main():
    wb = openpyxl.load_workbook('assets/works/Hotel List.xlsx')
    ws = wb['Paintings data']
    excel_rows = []
    for r in list(ws.iter_rows(values_only=True))[1:]:
        if any(cell is not None for cell in r):
            excel_rows.append({
                'cat': r[0],
                'priority': r[1],
                'name': r[2],
                'price': r[3],
                'size': r[4]
            })

    # Read files in assets/works
    works_dir = 'assets/works'
    folders = ['flowers', 'landscapes', 'watercolors', 'portraits', 'pets']
    
    # We will build a mapping of clean names to excel entries
    excel_map = {}
    for row in excel_rows:
        cat = row['cat'].lower() if row['cat'] else ""
        if cat == 'watercolors':
            cat = 'watercolours' # normalize to u spelling
        name = row['name']
        norm_name = normalize(name)
        if norm_name:
            excel_map[(cat, norm_name)] = row

    print("Excel entries count:", len(excel_rows))
    print("Excel entries with names:", len(excel_map))

    unmatched_files = []
    matched_count = 0

    for folder in folders:
        folder_path = os.path.join(works_dir, folder)
        if not os.path.exists(folder_path):
            print(f"Directory {folder} does not exist!")
            continue
        
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        print(f"\nCategory '{folder}' has {len(files)} files:")
        
        # Determine category key for matching
        match_cat = 'watercolours' if folder == 'watercolors' else folder
        
        for file in files:
            norm_file = normalize(file)
            # Try exact category match
            match = excel_map.get((match_cat, norm_file))
            if not match:
                # Try generic matching (just by name across all categories)
                candidates = [row for (c, nf), row in excel_map.items() if nf == norm_file]
                if candidates:
                    match = candidates[0]
            
            # Special case matching: e.g. "Costa Rican flowers.jpg" vs "Costa Rica flowers"
            if not match:
                # Let's see if we can do a substring or words match
                file_words = set(re.findall(r'\w+', file.split('.')[0].lower()))
                best_match = None
                best_score = 0
                for (c, nf), row in excel_map.items():
                    if c == match_cat:
                        row_words = set(re.findall(r'\w+', row['name'].lower()))
                        intersection = file_words.intersection(row_words)
                        if len(intersection) > best_score:
                            best_score = len(intersection)
                            best_match = row
                # If a significant overlap is found (e.g. 2 or more words, or 100% of row words)
                if best_match and best_score >= 2:
                    match = best_match

            if match:
                matched_count += 1
                # print(f"  Matched: '{file}' -> Excel: '{match['name']}' (Price: {match['price']}, Size: {match['size']}, Priority: {match['priority']})")
            else:
                unmatched_files.append((folder, file))
                print(f"  UNMATCHED: '{file}' (normalized: '{norm_file}')")

    print(f"\nTotal matched files: {matched_count}")
    print(f"Total unmatched files: {len(unmatched_files)}")

if __name__ == '__main__':
    main()
