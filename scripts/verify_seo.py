import json
import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Title & Meta
title_m = re.search(r'<title>(.*?)</title>', content)
title = title_m.group(1) if title_m else ""
desc_m = re.search(r'<meta name="description" content="(.*?)" />', content)
desc = desc_m.group(1) if desc_m else ""

print(f"Title: \"{title}\" (Length: {len(title)} chars - ideal is 40-60)")
print(f"Meta description: \"{desc}\" (Length: {len(desc)} chars - ideal is 130-160)")

# 2. H1 check
h1_tags = re.findall(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
print(f"H1 tags count: {len(h1_tags)}")
for h in h1_tags:
    print(f"  H1: {re.sub(r'<[^>]+>', '', h).strip()}")

# 3. Heading structure check (h5 tags)
h5_count = len(re.findall(r'<h5', content))
print(f"H5 tags count: {h5_count}")

# 4. JSON-LD Schemas
schemas = re.findall(r'<script type="application/ld\+json".*?>(.*?)</script>', content, re.DOTALL)
print(f"Total JSON-LD schemas: {len(schemas)}")

# 5. Alt Uniqueness in works.json
data = json.load(open("assets/works/works.json", encoding="utf-8"))
alts = [item["alt"] for item in data["_metadata"].values()]
print(f"Artwork Alt text count: {len(alts)}, Unique: {len(set(alts))}")

# 6. Sitemap check
with open("sitemap.xml", "r", encoding="utf-8") as f:
    sitemap = f.read()
print(f"Sitemap: {sitemap.count('<image:image>')} images, {sitemap.count('<url>')} url tags, Has '#' fragments: {'#' in sitemap}")
