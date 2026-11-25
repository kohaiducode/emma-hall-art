import os
import json
import re
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(ROOT, "index.html")
WORKS_JSON_PATH = os.path.join(ROOT, "assets", "works", "works.json")
BASE_URL = "https://www.emmahallpaintings.com"

CATEGORY_PATHS = {
    "watercolours": "assets/works/watercolours_brushed",
    "flowers": "assets/works/Flowers_brushed",
    "landscapes": "assets/works/landscapes_brushed",
    "pets": "assets/works/pets_brushed",
    "portraits": "assets/works/portraits_brushed"
}

CATEGORY_TITLES = {
    "flowers": "Botanical & Floral Oil Paintings",
    "landscapes": "Landscape & Travel Oil Paintings",
    "watercolours": "Original Watercolour Paintings",
    "portraits": "Fine Art & Figurative Portraits",
    "pets": "Custom Pet Portrait Paintings"
}

def escape_html(s):
    if not s:
        return ""
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&#39;"))

def parse_price_numeric(price_str):
    if not price_str:
        return None
    # Look for digits e.g. "550 €" -> 550
    m = re.search(r'(\d+)', price_str)
    if m:
        return m.group(1)
    return None

def build_artwork_schema(data):
    metadata = data.get("_metadata", {})
    item_list = []
    
    idx = 1
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
            size = meta.get("size", "")
            price = meta.get("price", "")
            status = meta.get("status", "")
            
            encoded_fn = urllib.parse.quote(filename).replace("%2C", ",").replace("%28", "(").replace("%29", ")")
            img_url = f"{BASE_URL}/{folder_base}/{encoded_fn}"
            
            is_sold = (status == "SOLD")
            price_num = parse_price_numeric(price)
            
            artwork_item = {
                "@type": "VisualArtwork",
                "name": name,
                "image": img_url,
                "description": alt,
                "artMedium": "Watercolour on paper" if cat == "watercolours" else "Oil on canvas",
                "artform": "Painting",
                "creator": {
                    "@id": f"{BASE_URL}/#artist"
                }
            }
            
            if size and size != 'x':
                artwork_item["width"] = size
                
            offers = {
                "@type": "Offer",
                "availability": "https://schema.org/SoldOut" if is_sold else "https://schema.org/InStock",
                "url": f"{BASE_URL}/"
            }
            if not is_sold and price_num:
                offers["price"] = price_num
                offers["priceCurrency"] = "EUR"
                
            artwork_item["offers"] = offers
            
            item_list.append({
                "@type": "ListItem",
                "position": idx,
                "item": artwork_item
            })
            idx += 1
            
    schema = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Original Paintings and Artworks by Emma Hall",
        "description": "Comprehensive catalog of original oil paintings, landscapes, botanicals, watercolours, portraits, and pet portrait commissions.",
        "numberOfItems": len(item_list),
        "itemListElement": item_list
    }
    return json.dumps(schema, indent=2, ensure_ascii=False)

def build_noscript_catalog(data):
    metadata = data.get("_metadata", {})
    lines = [
        '<noscript id="noscript-gallery-catalog">',
        '  <div class="noscript-catalog" style="padding: 24px 0; border-top: 1px solid #e6dccf; margin-top: 32px;">',
        '    <h3 style="font-family: \'Cormorant Garamond\', serif; font-size: 24px; margin-bottom: 16px;">Original Paintings &amp; Artworks Catalog</h3>',
        '    <p style="color: #6f635d; margin-bottom: 24px;">Explore original oil and watercolour paintings by visual artist Emma Hall, including landscapes from Italy, Japan, Lebanon, India, and the UK, vibrant botanical flora, fine art portraits, and custom pet commissions.</p>'
    ]
    
    for cat in ["flowers", "landscapes", "watercolours", "portraits", "pets"]:
        files = data.get(cat, [])
        folder_base = CATEGORY_PATHS.get(cat)
        cat_title = CATEGORY_TITLES.get(cat, cat.capitalize())
        
        lines.append(f'    <div class="noscript-category" style="margin-bottom: 32px;">')
        lines.append(f'      <h4 style="font-family: \'Cormorant Garamond\', serif; font-size: 20px; color: #2f2a28; margin-bottom: 12px; border-bottom: 1px solid #e6dccf; padding-bottom: 6px;">{cat_title} ({len(files)} works)</h4>')
        lines.append('      <ul style="list-style: none; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px;">')
        
        for filename in files:
            key = f"{cat}/{filename}"
            meta = metadata.get(key, {})
            name = escape_html(meta.get("name", filename.rsplit(".", 1)[0]))
            alt = escape_html(meta.get("alt", f"{name} - Original painting by Emma Hall"))
            size = escape_html(meta.get("size", ""))
            price = escape_html(meta.get("price", ""))
            status = meta.get("status", "")
            
            encoded_fn = urllib.parse.quote(filename).replace("%2C", ",").replace("%28", "(").replace("%29", ")")
            img_rel = f"{folder_base}/{encoded_fn}"
            
            meta_parts = []
            if size and size != 'x':
                meta_parts.append(f"{size} cm")
            if status == "SOLD":
                meta_parts.append('<strong style="color: #b86b5e;">SOLD</strong>')
            elif price and price != 'x':
                meta_parts.append(price)
            meta_str = " • ".join(meta_parts)
            
            lines.append('        <li style="background: #fffaf3; border: 1px solid #e6dccf; border-radius: 4px; overflow: hidden; padding: 10px;">')
            lines.append(f'          <img src="{img_rel}" alt="{alt}" loading="lazy" style="width: 100%; aspect-ratio: 1/1; object-fit: cover; display: block; border-radius: 2px; margin-bottom: 8px;" />')
            lines.append(f'          <h5 style="margin: 0 0 4px 0; font-size: 15px; color: #2f2a28;">{name}</h5>')
            if meta_str:
                lines.append(f'          <p style="margin: 0; font-size: 13px; color: #6f635d;">{meta_str}</p>')
            lines.append('        </li>')
            
        lines.append('      </ul>')
        lines.append('    </div>')
        
    lines.append('  </div>')
    lines.append('</noscript>')
    return "\n".join(lines)

def update_index_seo():
    with open(WORKS_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        html = f.read()
        
    # 1. Update Head Meta Tags
    title_text = "Emma Hall — Original Oil &amp; Watercolour Paintings | Landscapes, Botanicals &amp; Portraits"
    desc_text = "Explore original oil and watercolour paintings by Emma Hall. Featuring Italian &amp; Japanese landscapes, English roses, botanical floral art, fine art portraits, and custom pet commissions."
    keywords_text = "Emma Hall, Emma Hall paintings, original oil paintings, watercolour paintings, palette knife art, Italian landscapes, Japan paintings, botanical floral art, English roses, fine art portraits, custom pet portraits, art commissions"
    
    html = re.sub(r'<title>.*?</title>', f'<title>{title_text}</title>', html, count=1)
    html = re.sub(r'<meta name="description" content=".*?" />', f'<meta name="description" content="{desc_text}" />', html, count=1)
    html = re.sub(r'<meta name="keywords" content=".*?" />', f'<meta name="keywords" content="{keywords_text}" />', html, count=1)
    html = re.sub(r'<meta property="og:title" content=".*?" />', f'<meta property="og:title" content="{title_text}" />', html, count=1)
    html = re.sub(r'<meta property="og:description" content=".*?" />', f'<meta property="og:description" content="{desc_text}" />', html, count=1)
    html = re.sub(r'<meta name="twitter:title" content=".*?" />', f'<meta name="twitter:title" content="{title_text}" />', html, count=1)
    html = re.sub(r'<meta name="twitter:description" content=".*?" />', f'<meta name="twitter:description" content="{desc_text}" />', html, count=1)
    
    # 2. Update knowsAbout in JSON-LD Profile
    knows_about_snippet = '''"knowsAbout": [
            "Oil painting",
            "Watercolour paintings",
            "Palette knife and impasto techniques",
            "Italian landscapes (Venice, Tuscany, Ischia)",
            "Japanese landscapes & watercolours (Kyoto, Tokyo, Gion, Kinkakuji)",
            "Middle Eastern landscapes (Lebanon)",
            "Indian landscapes and river scenes",
            "British and European landscapes (London, France)",
            "Botanical and floral oil paintings (English roses, Sunflowers, Lilies, Pivoines)",
            "Fine art portraits and figurative paintings (David Bowie, classical copies)",
            "Custom pet portrait commissions (Dogs, cats)"
          ]'''
    html = re.sub(r'"knowsAbout":\s*\[.*?\]', knows_about_snippet, html, flags=re.DOTALL, count=1)
    
    # 3. Inject / Update VisualArtwork JSON-LD
    artwork_schema_json = build_artwork_schema(data)
    schema_block = f'<script type="application/ld+json" id="artwork-catalog-schema">\n{artwork_schema_json}\n  </script>'
    
    if 'id="artwork-catalog-schema"' in html:
        html = re.sub(r'<script type="application/ld\+json" id="artwork-catalog-schema">.*?</script>', schema_block, html, flags=re.DOTALL, count=1)
    else:
        # Insert before </head>
        html = html.replace('</head>', f'  {schema_block}\n</head>', 1)
        
    # 4. Inject / Update Noscript Catalog
    noscript_block = build_noscript_catalog(data)
    if 'id="noscript-gallery-catalog"' in html:
        html = re.sub(r'<noscript id="noscript-gallery-catalog">.*?</noscript>', noscript_block, html, flags=re.DOTALL, count=1)
    else:
        # Insert after <div id="gallery" class="grid" aria-live="polite"></div>
        target = '<div id="gallery" class="grid" aria-live="polite"></div>'
        html = html.replace(target, f'{target}\n\n        {noscript_block}', 1)
        
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"Successfully updated SEO elements in {INDEX_PATH}")

if __name__ == "__main__":
    update_index_seo()
