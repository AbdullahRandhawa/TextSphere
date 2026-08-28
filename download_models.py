"""
download_models.py — Download TextSphere fine-tuned models from Google Drive.

Usage:
    python download_models.py              # download all missing models
    python download_models.py --force      # re-download even if already present
    python download_models.py --model ner  # download a single model

Prerequisites:
    pip install gdown

How to get your Google Drive file/folder IDs:
    1. Upload your model folder to Google Drive
    2. Right-click → Share → "Anyone with the link"
    3. Copy the link — it looks like:
       https://drive.google.com/drive/folders/1ABCdef...XYZ?usp=sharing
    4. The ID is the part after /folders/  (or /file/d/ for single files)
    5. Paste that ID into DRIVE_IDS below.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# ⚙️  CONFIGURE YOUR GOOGLE DRIVE FOLDER IDs HERE
#     Replace the placeholder strings with your real folder IDs from Drive.
#     Each entry should be a shared folder containing all files for that model.
# ---------------------------------------------------------------------------
DRIVE_IDS: dict[str, str] = {
    "sentiment":     "PASTE_YOUR_DRIVE_FOLDER_ID_FOR_SENTIMENT_HERE",
    "topic":         "PASTE_YOUR_DRIVE_FOLDER_ID_FOR_TOPIC_HERE",
    "ner":           "PASTE_YOUR_DRIVE_FOLDER_ID_FOR_NER_HERE",
    "summarization": "PASTE_YOUR_DRIVE_FOLDER_ID_FOR_SUMMARIZATION_HERE",
    "qa":            "PASTE_YOUR_DRIVE_FOLDER_ID_FOR_QA_HERE",
}

# Destination: backend/app/finetuned_models/<model_name>/
ROOT        = Path(__file__).parent
MODELS_BASE = ROOT / "backend" / "app" / "finetuned_models"

OK   = "\033[92m[OK]\033[0m"
ERR  = "\033[91m[X]\033[0m"
INFO = "\033[94m[~]\033[0m"
WARN = "\033[93m[!]\033[0m"


def check_gdown() -> bool:
    try:
        import gdown  # noqa: F401
        return True
    except ImportError:
        print(f"\n  {ERR}  'gdown' is not installed.")
        print("       Run:  pip install gdown\n")
        return False


def model_is_present(dest: Path) -> bool:
    """Returns True if the destination folder has at least one .safetensors file."""
    if not dest.exists():
        return False
    return any(dest.glob("*.safetensors"))


def download_model(name: str, folder_id: str, dest: Path, force: bool) -> bool:
    """Download a model folder from Google Drive using gdown."""
    import gdown

    if folder_id.startswith("PASTE_"):
        print(f"  {WARN}  {name}: Drive ID not configured — skipping.")
        print(f"       Edit DRIVE_IDS in download_models.py and add your folder ID.")
        return False

    if model_is_present(dest) and not force:
        print(f"  {OK}  {name}: already present at {dest}  (use --force to re-download)")
        return True

    if dest.exists() and force:
        print(f"  {INFO}  {name}: removing existing files for re-download ...")
        shutil.rmtree(dest)

    dest.mkdir(parents=True, exist_ok=True)
    url = f"https://drive.google.com/drive/folders/{folder_id}"

    print(f"\n  {INFO}  {name}: downloading from Google Drive ...")
    print(f"       Folder ID : {folder_id}")
    print(f"       Saving to : {dest}\n")

    try:
        gdown.download_folder(url=url, output=str(dest), quiet=False, use_cookies=False)
        if model_is_present(dest):
            print(f"\n  {OK}  {name}: download complete!\n")
            return True
        else:
            print(f"\n  {ERR}  {name}: download finished but no .safetensors found.")
            print("       Check that your Drive folder is shared as 'Anyone with the link'.")
            return False
    except Exception as exc:
        print(f"\n  {ERR}  {name}: download failed — {exc}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download TextSphere fine-tuned models from Google Drive."
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Re-download models even if they are already present."
    )
    parser.add_argument(
        "--model", metavar="NAME", choices=list(DRIVE_IDS.keys()),
        help="Download only a specific model (choices: %(choices)s)."
    )
    args = parser.parse_args()

    print("\n=== TextSphere Model Downloader =====================================")
    print(f"    Models will be saved to: {MODELS_BASE}\n")

    if not check_gdown():
        sys.exit(1)

    targets = {args.model: DRIVE_IDS[args.model]} if args.model else DRIVE_IDS

    results: dict[str, bool] = {}
    for name, folder_id in targets.items():
        dest = MODELS_BASE / name
        results[name] = download_model(name, folder_id, dest, force=args.force)

    # Summary
    print("\n=== Summary ==========================================================")
    passed = sum(results.values())
    total  = len(results)
    for name, ok in results.items():
        icon = OK if ok else ERR
        print(f"  {icon}  {name}")

    print()
    if passed == total:
        print(f"  {OK}  All {total} model(s) ready!")
        print("       You can now start the backend:")
        print("       cd backend && uvicorn app.main:app --reload")
    else:
        failed = total - passed
        print(f"  {ERR}  {failed} model(s) failed or not configured.")
        print("       See messages above for details.")
    print()
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
