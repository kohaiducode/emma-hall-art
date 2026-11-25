import json
import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

schemas = re.findall(r'<script type="application/ld\+json".*?>(.*?)</script>', content, re.DOTALL)
print(f"Total JSON-LD schemas found: {len(schemas)}")
for i, s in enumerate(schemas):
    try:
        data = json.loads(s.strip())
        schema_type = data.get("@type", "Graph" if "@graph" in data else "Unknown")
        print(f"  Schema #{i+1}: Valid JSON (Type: {schema_type})")
        if "@graph" in data:
            print(f"    Graph contains {len(data['@graph'])} entities: {[e.get('@type') for e in data['@graph']]}")
        elif schema_type == "ItemList":
            print(f"    ItemList contains {data.get('numberOfItems')} artwork items.")
    except Exception as e:
        print(f"  Schema #{i+1}: ERROR - {e}")

# Check noscript
has_noscript = '<noscript id="noscript-gallery-catalog">' in content
print(f"Noscript catalog present: {has_noscript}")
if has_noscript:
    # count items inside noscript
    items = re.findall(r'<li style=', content)
    print(f"Noscript catalog contains {len(items)} items.")

# Check meta description
m_desc = re.search(r'<meta name="description" content="(.*?)" />', content)
if m_desc:
    print(f"Meta description: {m_desc.group(1)[:80]}...")

# Check sitemap
with open("sitemap.xml", "r", encoding="utf-8") as f:
    sitemap = f.read()
img_count = sitemap.count("<image:image>")
url_count = sitemap.count("<url>")
has_fragments = "#" in sitemap
print(f"Sitemap check: {url_count} <url> entries, {img_count} images. Has fragments: {has_fragments}")
