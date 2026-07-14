#!/usr/bin/env python3
"""
Skripta za sortiranje fotografija/videa po datumu kreiranja i pronalaženje duplikata.

ŠTA RADI:
- Prolazi kroz SOURCE_FOLDER i sve njegove podfoldere
- Za svaki fajl (sliku/video) pokušava da nađe pravi datum snimanja (EXIF/metadata),
  a ako ga nema, koristi datum fajla na disku
- Prepoznaje duplikate poredeći SADRŽAJ fajla (hash), ne samo ime
- Kopira sve JEDINSTVENE fajlove u OUTPUT_FOLDER, preimenovane sa datumom na početku
  imena (npr. 2024-03-15_14-30-00_IMG1234.jpg) tako da su hronološki sortirani po imenu
- Duplikate NE BRIŠE automatski iz originala - pravi log fajl da ih prvo pregledaš

ZAHTEVA:
- Python 3 (već je na Mac-u)
- exiftool -> instaliraj sa: brew install exiftool
  (ako nemaš Homebrew: https://brew.sh)
"""

import subprocess
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime

# ===================== PODESI OVO PRE POKRETANJA =====================
SOURCE_FOLDER = "/Users/tamara/Desktop/Uspomene"       # folder sa svim slikama/videima (i podfolderima)
OUTPUT_FOLDER = "/Users/tamara/Desktop/sortSlike"    # gde ide sortiran, deduplikovan rezultat
DELETE_DUPLICATES_FROM_SOURCE = False   # promeni u True TEK NAKON što pregledaš duplikati_log.txt
# ========================================================================

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".gif", ".tiff", ".bmp"}
VIDEO_EXTS = {".mov", ".mp4", ".m4v", ".avi"}


def get_all_files(folder):
    return [p for p in Path(folder).rglob("*")
            if p.is_file() and p.suffix.lower() in IMAGE_EXTS | VIDEO_EXTS]


def get_date(filepath):
    """Uzima pravi datum snimanja koristeći exiftool, uz fallback na datum fajla na disku."""
    try:
        result = subprocess.run(
            ["exiftool", "-j", "-DateTimeOriginal", "-CreateDate",
             "-MediaCreateDate", "-FileModifyDate", str(filepath)],
            capture_output=True, text=True, check=True
        )
        data = json.loads(result.stdout)[0]
        for key in ("DateTimeOriginal", "CreateDate", "MediaCreateDate", "FileModifyDate"):
            if key in data and data[key]:
                date_str = str(data[key]).split("+")[0].strip()
                try:
                    return datetime.strptime(date_str[:19], "%Y:%m:%d %H:%M:%S")
                except ValueError:
                    continue
    except Exception:
        pass
    # fallback - datum fajla na disku ako exiftool ne uspe ili nije instaliran
    return datetime.fromtimestamp(filepath.stat().st_mtime)


def file_hash(filepath, chunk_size=8192):
    """Računa SHA256 hash sadržaja fajla da bi se prepoznali pravi duplikati."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    source = Path(SOURCE_FOLDER)
    output = Path(OUTPUT_FOLDER)

    if not source.exists():
        print(f"GREŠKA: folder ne postoji: {source}")
        print("Proveri putanju u SOURCE_FOLDER na vrhu skripte.")
        return

    output.mkdir(parents=True, exist_ok=True)

    files = get_all_files(source)
    print(f"Pronađeno {len(files)} fajlova (slika/videa).\n")

    print("Računam datume i hash-eve (ovo može potrajati za veliki broj fajlova)...")
    file_info = []
    for i, f in enumerate(files, 1):
        date = get_date(f)
        h = file_hash(f)
        file_info.append({"path": f, "date": date, "hash": h})
        if i % 50 == 0:
            print(f"  ...obrađeno {i}/{len(files)}")

    # Grupisanje po hash-u - prepoznavanje duplikata (zadržava se najstariji primerak)
    seen_hashes = {}
    duplicates = []
    unique_files = []
    for info in sorted(file_info, key=lambda x: x["date"]):
        if info["hash"] in seen_hashes:
            duplicates.append(info)
        else:
            seen_hashes[info["hash"]] = info
            unique_files.append(info)

    print(f"\nJedinstvenih fajlova: {len(unique_files)}")
    print(f"Duplikata pronađeno: {len(duplicates)}")

    # Kopiranje jedinstvenih fajlova, sortiranih hronološki, sa datumom u imenu
    unique_files.sort(key=lambda x: x["date"])
    for info in unique_files:
        date_str = info["date"].strftime("%Y-%m-%d_%H-%M-%S")
        new_name = f"{date_str}_{info['path'].name}"
        dest = output / new_name
        counter = 1
        while dest.exists():
            new_name = f"{date_str}_{counter}_{info['path'].name}"
            dest = output / new_name
            counter += 1
        shutil.copy2(info["path"], dest)

    print(f"\nGotovo. Sortirani, deduplikovani fajlovi su u:\n  {output}")

    # Log fajl sa listom duplikata za pregled
    log_path = output.parent / "duplikati_log.txt"
    with open(log_path, "w") as log:
        log.write(f"Pronađeno {len(duplicates)} duplikata (identičan sadržaj fajla kao neki drugi fajl):\n\n")
        for d in duplicates:
            original = seen_hashes[d["hash"]]["path"]
            log.write(f"DUPLIKAT: {d['path']}\n  (isti sadržaj kao: {original})\n\n")
    print(f"Lista duplikata sačuvana u:\n  {log_path}")

    if DELETE_DUPLICATES_FROM_SOURCE:
        print("\nBrišem duplikate iz originalnog foldera...")
        for d in duplicates:
            d["path"].unlink()
        print(f"Obrisano {len(duplicates)} duplikata iz originala.")
    else:
        print("\nDuplikati NISU obrisani iz originalnog foldera (DELETE_DUPLICATES_FROM_SOURCE = False).")
        print("Prvo pregledaj 'Fotografije_Sortirano' folder i duplikati_log.txt.")
        print("Ako je sve u redu, promeni DELETE_DUPLICATES_FROM_SOURCE na True i pokreni skriptu ponovo.")


if __name__ == "__main__":
    main()
