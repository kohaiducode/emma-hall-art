// scripts/build-works-manifest.mjs
import { promises as fs } from "node:fs";
import path from "node:path";

const ROOT = process.cwd();
const WORKS_ROOT = path.join(ROOT, "assets", "works");

// Keep these in sync with your UI chips
const CATEGORIES = ["aquarelles", "flowers", "landscapes", "pets", "portraits"];

// Which files to include
const IMG_EXT = new Set([".jpg", ".jpeg", ".png", ".webp", ".gif"]);

async function listImages(dir) {
    try {
        const items = await fs.readdir(dir, { withFileTypes: true });
        return items
            .filter(d => d.isFile() && IMG_EXT.has(path.extname(d.name).toLowerCase()))
            .map(d => d.name)
            .sort((a, b) => a.localeCompare(b, undefined, { numeric: true, sensitivity: "base" }));
    } catch (e) {
        // directory might not exist yet — treat as empty
        return [];
    }
}

async function main() {
    const manifest = {};
    for (const cat of CATEGORIES) {
        const dir = path.join(WORKS_ROOT, cat);
        manifest[cat] = await listImages(dir);
    }

    const outPath = path.join(WORKS_ROOT, "works.json");
    await fs.mkdir(path.dirname(outPath), { recursive: true });
    await fs.writeFile(outPath, JSON.stringify(manifest, null, 2) + "\n", "utf8");

    console.log("Wrote", outPath);
    console.log(manifest);
}

main().catch(err => {
    console.error(err);
    process.exit(1);
});
