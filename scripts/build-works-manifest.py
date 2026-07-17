# scripts/build-works-manifest.py
import os
import json
import openpyxl
import re

ROOT = os.getcwd()
WORKS_ROOT = os.path.join(ROOT, "assets", "works")
EXCEL_PATH = os.path.join(WORKS_ROOT, "Hotel List.xlsx")

# Categories matching the folder names
CATEGORIES = ["flowers", "landscapes", "watercolours", "portraits", "pets"]
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# Map category key (used in UI and JSON) to physical folder name
CATEGORY_FOLDERS = {
    "flowers": "Flowers_brushed",
    "landscapes": "landscapes_brushed",
    "watercolours": "watercolours_brushed",
    "portraits": "portraits_brushed",
    "pets": "pets_brushed"
}

# Manual overrides for files (keys are filename without extension)
MANUAL_MAPPING = {
    # Flowers
    "PIVOINES of ile de france": "Pivoines",
    "The spring forest in velizy": "Spring V.",
    "Sunflowers of Tuscany": "Sunflowers from Tuscany",
    "Savoie flowers": "Savoie mountain flowers",
    "Leaves in the waters of Lake Annecy": "Leaves in Lake Annecy",
    "Purple japanese water lilies": "Purple Japanese water lily",
    "Sakura blowing in the blue skies of Tokyo": "Sakura flowers",
    
    # Landscapes
    "Flowing river in India": "River flowing in India ",
    "Hills in the Lebanon": "Hills in Lebanon",
    "Le sud ouest, France": "The south west of France",
    "Spring in the forest of Velizy, France": "Spring in Velizy, France",
    "The Bluebell girl": "The bluebell girl, London",
    "The Emperors Gardens, Kyoto, Japan": "Kyoto Emperors garden,",
    "Tokyoview from Shibuja": "Tokyo view from Shinjuku",
    "View on an Indian river": "View on India",
    "Where Sakura trees meet Tuscany": "Where Sakura meets Tuscany",
    
    # Watercolours
    "Hut in hills in Japan": "Hut in the hills",
    "japanese countrysidd": "Japanese countryside",
    "Pivoines, France": "Pivoines from France",
    "The small pink rose": "Small Rose"
}

def normalize(s):
    if not s:
        return ""
    # lowercase, remove extension, remove all non-alphanumeric characters
    s = s.split('.')[0]
    return re.sub(r'[^a-z0-9]', '', s.lower())

def humanize_name(filename):
    name = os.path.splitext(filename)[0]
    # Remove any trailing parenthetical copies e.g. "(1)"
    name = re.sub(r'\(\d+\)$', '', name)
    name = re.sub(r'[-_]+', ' ', name)
    # Clean up double spaces
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def format_price(p):
    if not p:
        return "Price on demand"
    p_str = str(p).strip()
    if p_str.lower() == 'x' or p_str.lower() == 'price on demand':
        return p_str
    
    # Normalize float string if it has .0
    if re.match(r'^\d+\.0+$', p_str):
        p_str = p_str.split('.')[0]
        
    # Replace case-insensitive ' E' or 'E' at the end of the string with ' €'
    # E.g. '450 E' -> '450 €', '450E' -> '450 €', 'around 250 E' -> 'around 250 €'
    p_str = re.sub(r'(?<=\d)\s*[eE]$|\b[eE]$', ' €', p_str)
    
    # If the price is purely numeric (like '300'), append ' €'
    if re.match(r'^\d+$', p_str):
        p_str = p_str + ' €'
        
    # Clean up multiple spaces
    formatted = re.sub(r'\s+', ' ', p_str).strip()
    
    # Normalize price on demand phrasing
    if formatted.lower() in ('price on demand', 'price on demand €'):
        return "Price on demand"
    return formatted

def main():
    # 1. Read Excel rows
    excel_rows = []
    if os.path.exists(EXCEL_PATH):
        wb = openpyxl.load_workbook(EXCEL_PATH)
        ws = wb['Paintings data']
        for r in list(ws.iter_rows(values_only=True))[1:]:
            if any(cell is not None for cell in r):
                excel_rows.append({
                    'category': str(r[0] or "").strip().lower(),
                    'filename': str(r[1] or "").strip(),
                    'name': str(r[2]).strip() if r[2] is not None else None,
                    'price': str(r[3]).strip() if r[3] is not None else None,
                    'size': str(r[4]).strip() if r[4] is not None else None,
                    'priority': str(r[5] or "No").strip().lower() == "yes",
                    'status': str(r[6]).strip() if len(r) > 6 and r[6] is not None else ""
                })
        print(f"Loaded {len(excel_rows)} rows from Excel.")
    else:
        print(f"Warning: Excel sheet not found at {EXCEL_PATH}. Proceeding with defaults.")

    # Group excel entries by category
    excel_by_cat = {}
    for row in excel_rows:
        cat = row['category']
        if cat == 'watercolors':
            cat = 'watercolours'
        excel_by_cat.setdefault(cat, []).append(row)

    # 2. Build metadata mapping and categorize local files
    manifest = {cat: [] for cat in CATEGORIES}
    metadata = {}

    for cat in CATEGORIES:
        folder_name = CATEGORY_FOLDERS.get(cat, cat)
        dir_path = os.path.join(WORKS_ROOT, folder_name)
        if not os.path.exists(dir_path):
            print(f"Warning: Directory {dir_path} does not exist.")
            continue

        # Get list of images
        files = []
        for f in os.listdir(dir_path):
            if os.path.isfile(os.path.join(dir_path, f)) and os.path.splitext(f)[1].lower() in IMG_EXT:
                files.append(f)

        print(f"Folder '{cat}' has {len(files)} files.")

        # Excel rows for this category
        cat_excel_rows = excel_by_cat.get(cat, [])
        
        # Build index maps for matching:
        # 1. Exact/clean filename matching
        file_map = {}
        # 2. Clean name matching
        name_map = {}
        
        for row in cat_excel_rows:
            if row['filename']:
                file_map[normalize(row['filename'])] = row
            if row['name']:
                name_map[normalize(row['name'])] = row

        for filename in files:
            matched_row = None
            filename_no_ext = os.path.splitext(filename)[0]

            # Hierarchical matching:
            # 1. Try exact/clean matching on File Name column
            matched_row = file_map.get(normalize(filename))

            # 2. Try clean matching on filename without extension
            if not matched_row:
                matched_row = file_map.get(normalize(filename_no_ext))

            # 3. Try clean matching on Display Name (Name) column using full filename
            if not matched_row:
                matched_row = name_map.get(normalize(filename))

            # 4. Try clean matching on Display Name (Name) column using filename without extension
            if not matched_row:
                matched_row = name_map.get(normalize(filename_no_ext))

            # 5. Try manual mapping override as a fallback
            if not matched_row:
                matched_name = MANUAL_MAPPING.get(filename_no_ext)
                if matched_name:
                    matched_row = name_map.get(normalize(matched_name))

            # 6. Try fuzzy matching (substring search on clean Name)
            if not matched_row:
                norm_file = normalize(filename)
                for clean_name, row in name_map.items():
                    if clean_name in norm_file or norm_file in clean_name:
                        matched_row = row
                        break

            # Construct metadata
            meta_key = f"{cat}/{filename}"
            if matched_row:
                metadata[meta_key] = {
                    'name': matched_row['name'] if matched_row['name'] else humanize_name(filename),
                    'price': format_price(matched_row['price']),
                    'size': matched_row['size'] or "",
                    'priority': matched_row['priority'],
                    'status': matched_row.get('status', '')
                }
            else:
                # Complete fallback
                metadata[meta_key] = {
                    'name': humanize_name(filename),
                    'price': "Price on demand",
                    'size': "",
                    'priority': False,
                    'status': ""
                }

            manifest[cat].append(filename)

    # 3. Sort files inside each category by visual priority
    for cat in CATEGORIES:
        files = manifest[cat]
        # Sort key: (not priority, filename) - since priority (True) sorted first
        def sort_key(f):
            meta = metadata[f"{cat}/{f}"]
            return (not meta['priority'], meta['name'].lower())
        
        files.sort(key=sort_key)
        manifest[cat] = files

    # 4. Generate visual priority ordering for the "All" view
    # Group categories: Group 1 (priority categories) and Group 2 (last categories)
    GROUP_1 = ["flowers", "landscapes", "watercolours"]
    GROUP_2 = ["portraits", "pets"]

    # Gather priority and non-priority paintings for each category
    prio_by_cat = {cat: [] for cat in CATEGORIES}
    non_prio_by_cat = {cat: [] for cat in CATEGORIES}

    for cat in CATEGORIES:
        for f in manifest[cat]:
            key = f"{cat}/{f}"
            if metadata[key]['priority']:
                prio_by_cat[cat].append(key)
            else:
                non_prio_by_cat[cat].append(key)

    # Sort each list alphabetically by name
    for cat in CATEGORIES:
        prio_by_cat[cat].sort(key=lambda k: metadata[k]['name'].lower())
        non_prio_by_cat[cat].sort(key=lambda k: metadata[k]['name'].lower())

    # Helper function to interleave lists of categories
    def interleave(cats, data_dict):
        lists = [list(data_dict[c]) for c in cats if data_dict[c]]
        result = []
        max_len = max((len(lst) for lst in lists), default=0)
        for i in range(max_len):
            for lst in lists:
                if i < len(lst):
                    result.append(lst[i])
        return result

    # Interleave priority paintings: Group 1 first, then Group 2
    prio_g1 = interleave(GROUP_1, prio_by_cat)
    prio_g2 = interleave(GROUP_2, prio_by_cat)

    # Interleave non-priority paintings: Group 1 first, then Group 2
    non_prio_g1 = interleave(GROUP_1, non_prio_by_cat)
    non_prio_g2 = interleave(GROUP_2, non_prio_by_cat)

    # Combine all in the desired order
    all_paintings = prio_g1 + prio_g2 + non_prio_g1 + non_prio_g2
    manifest['_allOrder'] = all_paintings

    # Add metadata to the manifest
    manifest['_metadata'] = metadata

    # 5. Write to works.json
    out_path = os.path.join(WORKS_ROOT, "works.json")
    with open(out_path, "w", encoding="utf8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Successfully wrote manifest to {out_path}")
    
    # Print priority count details
    priority_count = sum(1 for k, v in metadata.items() if v['priority'])
    print(f"Total paintings: {len(all_paintings)}, Priority paintings: {priority_count}")

if __name__ == "__main__":
    main()
