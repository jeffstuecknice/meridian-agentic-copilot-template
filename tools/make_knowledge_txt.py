"""Generate Knowledge-Store upload copies: knowledge/*.md -> knowledge/upload/*.txt

The Cognigy Knowledge Store accepts .txt but not .md. Markdown stays the authored
source of truth; run this after any policy edit, then re-upload the changed doc(s).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "knowledge"
OUT = SRC / "upload"


def main():
    OUT.mkdir(exist_ok=True)
    docs = sorted(SRC.glob("MER-POL-*.md"))
    if not docs:
        raise SystemExit("no MER-POL-*.md docs found in knowledge/")
    for md in docs:
        txt = OUT / (md.stem + ".txt")
        txt.write_text(md.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
        print(f"wrote {txt.relative_to(ROOT)}")
    print(f"{len(docs)} docs ready in knowledge/upload/")


if __name__ == "__main__":
    main()
