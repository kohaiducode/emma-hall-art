# scripts/optimize_images.py
import os
import re
from PIL import Image

ROOT = os.getcwd()
WORKS_ROOT = os.path.join(ROOT, "assets", "works")

CATEGORY_FOLDERS = [
    "Flowers_brushed",
    "landscapes_brushed",
    "watercolours_brushed",
    "portraits_brushed",
    "pets_brushed"
]

MAX_DIM = 1200  # maximum width or height in pixels
QUALITY = 82    # WebP compression quality

def main():
    total_before = 0
    total_after = 0
    optimized_count = 0
    skipped_count = 0

    print("Starting image optimization process...")
    print(f"Target maximum dimension: {MAX_DIM}px, WebP Quality: {QUALITY}%\n")

    for folder in CATEGORY_FOLDERS:
        folder_path = os.path.join(WORKS_ROOT, folder)
        if not os.path.exists(folder_path):
            print(f"Warning: Folder {folder_path} does not exist. Skipping.")
            continue

        print(f"Optimizing folder: {folder}...")
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            if not os.path.isfile(filepath):
                continue

            name, ext = os.path.splitext(filename)
            ext = ext.lower()
            if ext not in {".png", ".jpg", ".jpeg", ".webp"}:
                continue

            size_before = os.path.getsize(filepath)
            total_before += size_before

            # We want to output to a .webp file
            webp_filename = f"{name}.webp"
            webp_filepath = os.path.join(folder_path, webp_filename)

            try:
                with Image.open(filepath) as img:
                    width, height = img.size
                    
                    # Check if resizing is needed
                    needs_resize = width > MAX_DIM or height > MAX_DIM
                    needs_conversion = ext != ".webp"

                    if not needs_resize and not needs_conversion:
                        # File is already webp and within size limits, skip
                        # but keep track of its size
                        total_after += size_before
                        skipped_count += 1
                        continue

                    # Resize preserving aspect ratio
                    if needs_resize:
                        if width > height:
                            new_width = MAX_DIM
                            new_height = int(height * (MAX_DIM / width))
                        else:
                            new_height = MAX_DIM
                            new_width = int(width * (MAX_DIM / height))
                        
                        # Use Resampling.LANCZOS for high quality downscaling
                        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        print(f"  Resizing '{filename}' from {width}x{height} to {new_width}x{new_height}")
                    else:
                        img_resized = img

                    # Save as WebP
                    img_resized.save(webp_filepath, "WEBP", quality=QUALITY)
                    
                size_after = os.path.getsize(webp_filepath)
                total_after += size_after
                optimized_count += 1

                # If we created a new file and the old file has a different extension, delete old file
                if filepath != webp_filepath:
                    os.remove(filepath)
                    print(f"  Optimized: '{filename}' ({size_before/1024/1024:.2f}MB) -> '{webp_filename}' ({size_after/1024:.1f}KB)")
                else:
                    print(f"  Resized: '{filename}' ({size_before/1024/1024:.2f}MB) -> ({size_after/1024:.1f}KB)")

            except Exception as e:
                print(f"  Error processing '{filename}': {e}")
                # Keep original size in totals if failed
                total_after += size_before

        print(f"Finished {folder}\n")

    mb_before = total_before / 1024 / 1024
    mb_after = total_after / 1024 / 1024
    savings = mb_before - mb_after
    savings_pct = (savings / mb_before * 100) if mb_before > 0 else 0

    print("=" * 50)
    print("Optimization Summary:")
    print(f"Total images processed/optimized: {optimized_count}")
    print(f"Total images skipped (already optimized WebP): {skipped_count}")
    print(f"Total size BEFORE: {mb_before:.2f} MB")
    print(f"Total size AFTER:  {mb_after:.2f} MB")
    print(f"Saved:             {savings:.2f} MB ({savings_pct:.1f}% reduction)")
    print("=" * 50)

if __name__ == "__main__":
    main()
