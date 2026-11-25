import os
import json
import urllib.parse
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKS_JSON_PATH = os.path.join(ROOT, "assets", "works", "works.json")
SITEMAP_PATH = os.path.join(ROOT, "sitemap.xml")
BASE_URL = "https://www.emmahallpaintings.com"

CATEGORY_PATHS = {
    "watercolours": "assets/works/watercolours_brushed",
    "flowers": "assets/works/Flowers_brushed",
    "landscapes": "assets/works/landscapes_brushed",
    "pets": "assets/works/pets_brushed",
    "portraits": "assets/works/portraits_brushed"
}

def escape_xml(s):
    if not s:
        return ""
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&apos;"))

def generate_sitemap():
    today = datetime.now().strftime("%Y-%m-%d")
    
    with open(WORKS_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    metadata = data.get("_metadata", {})
    
    # Collect all image entries
    images = []
    
    # 1. Profile / Bio Images
    profile_images = [
        ("assets/profile/ems.jpg", "Emma Hall in Studio", "Emma Hall — Visual Artist and Painter in her Studio"),
        ("assets/profile/1.webp", "Emma Hall Article and Feature Exhibition Paintings", "Emma Hall press feature and exhibition oil paintings"),
        ("assets/profile/2.webp", "Emma Hall Portrait", "Emma Hall Portrait — Contemporary Artist"),
        ("assets/profile/3.webp", "Emma Hall Studio Workspace", "Emma Hall Studio Workspace and Palette Knife Artwork")
    ]
    for rel_path, title, caption in profile_images:
        images.append({
            "loc": f"{BASE_URL}/{rel_path}",
            "title": title,
            "caption": caption
        })
        
    # 2. Artwork Images
    for cat, files in data.items():
        if cat in ('_allOrder', '_metadata'):
            continue
        folder_base = CATEGORY_PATHS.get(cat)
        if not folder_base:
            continue
        for filename in files:
            key = f"{cat}/{filename}"
            meta = metadata.get(key, {})
            name = meta.get("name", filename.rsplit(".", 1)[0])
            alt = meta.get("alt", f"{name} - Original {'watercolour' if cat == 'watercolours' else 'oil'} painting by Emma Hall")
            
            # URL quote filename preserving commas and parens like in index.html
            encoded_fn = urllib.parse.quote(filename).replace("%2C", ",").replace("%28", "(").replace("%29", ")")
            img_url = f"{BASE_URL}/{folder_base}/{encoded_fn}"
            images.append({
                "loc": img_url,
                "title": name,
                "caption": alt
            })

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
        '  <!-- Homepage with Google Image Indexation -->',
        '  <url>',
        f'    <loc>{BASE_URL}/</loc>',
        f'    <lastmod>{today}</lastmod>',
        '    <changefreq>weekly</changefreq>',
        '    <priority>1.0</priority>'
    ]

    for img in images:
        xml_lines.append('    <image:image>')
        xml_lines.append(f'      <image:loc>{escape_xml(img["loc"])}</image:loc>')
        xml_lines.append(f'      <image:title>{escape_xml(img["title"])}</image:title>')
        xml_lines.append(f'      <image:caption>{escape_xml(img["caption"])}</image:caption>')
        xml_lines.append('    </image:image>')

    xml_lines.append('  </url>')
    xml_lines.append('</urlset>')
    xml_lines.append('')

    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(xml_lines))

    print(f"Generated {SITEMAP_PATH} with {len(images)} images.")

if __name__ == "__main__":
    generate_sitemap()
