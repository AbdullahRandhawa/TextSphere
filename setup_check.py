"""
setup_check.py — Run this script from the workspace root to verify
that the TextSphere backend is ready to start.

Usage:
    python setup_check.py
"""

import os
import sys
import shutil
from pathlib import Path

ROOT    = Path(__file__).parent
BACKEND  = ROOT / "backend"
FRONTEND = ROOT / "frontend"

OK   = "[OK]"
WARN = "[!] "
ERR  = "[X] "


def check(label, ok, hint=""):
    icon = OK if ok else ERR
    print(f"  {icon}  {label}")
    if not ok and hint:
        print(f"       -> {hint}")
    return ok


issues = 0

print("\n=== TextSphere Setup Check ===================================")

# ── 1. Model folders ──────────────────────────────────────────────
print("\n[1] Fine-tuned model folders (backend/app/finetuned_models/)")
FINETUNED = BACKEND / "app" / "finetuned_models"
models = {
    "sentiment":     FINETUNED / "sentiment",
    "topic":         FINETUNED / "topic",
    "ner":           FINETUNED / "ner",
    "summarization": FINETUNED / "summarization",
    "qa":            FINETUNED / "qa",
}
for name, path in models.items():
    # Check for at least one .safetensors weight file
    has_weights = path.exists() and any(path.glob("*.safetensors"))
    check(f"{name:<16} {path.relative_to(ROOT)}", has_weights,
          f"Missing! Run: python download_models.py --model {name}" if not has_weights else "")
    if not has_weights:
        issues += 1

if issues > 0:
    print("\n  Tip: download ALL missing models at once with:")
    print("       pip install gdown && python download_models.py")
    print("       (configure your Google Drive IDs in download_models.py first)\n")

# ── 2. Firebase credentials JSON ──────────────────────────────────
print("\n[2] Firebase service-account JSON")
cred_path = BACKEND / "firebase_credentials.json"
found_json = None

# Search for adminsdk JSONs in project root and frontend
for search_dir in [ROOT, FRONTEND]:
    for f in search_dir.glob("*adminsdk*.json"):
        found_json = f
        break
    if found_json:
        break

if cred_path.exists():
    check("backend/firebase_credentials.json exists", True)
elif found_json:
    print(f"  {WARN} Found credentials at: {found_json}")
    print(f"       -> Moving to backend/firebase_credentials.json ...")
    shutil.move(str(found_json), str(cred_path))
    print(f"  {OK}  Moved successfully!")
else:
    check("backend/firebase_credentials.json", False,
          "Download from Firebase Console -> Service Accounts -> Generate new private key\n"
          "       Save as: backend/firebase_credentials.json")
    issues += 1

# ── 3. Backend .env ───────────────────────────────────────────────
print("\n[3] Backend .env")
backend_env = BACKEND / ".env"
if backend_env.exists() and backend_env.stat().st_size > 10:
    content = backend_env.read_text(encoding="utf-8", errors="ignore")
    has_key = "OPENROUTER_API_KEY=sk-" in content
    check("backend/.env is non-empty", True)
    check("OPENROUTER_API_KEY is set", has_key,
          "Add OPENROUTER_API_KEY=sk-or-... to backend/.env")
    if not has_key:
        issues += 1
else:
    check("backend/.env", False,
          "Copy backend/.env.example -> backend/.env and fill in your keys")
    issues += 1

# ── 4. Frontend .env ──────────────────────────────────────────────
print("\n[4] Frontend .env")
frontend_env = FRONTEND / ".env"
if frontend_env.exists() and frontend_env.stat().st_size > 10:
    content = frontend_env.read_text(encoding="utf-8", errors="ignore")
    has_api_key = "VITE_FIREBASE_API_KEY=AIza" in content
    check("frontend/.env is non-empty", True)
    check("VITE_FIREBASE_API_KEY is set", has_api_key,
          "Fill in all VITE_FIREBASE_* values from Firebase Console -> Project Settings -> Your apps")
    if not has_api_key:
        issues += 1
else:
    check("frontend/.env", False,
          "Copy frontend/.env.example -> frontend/.env and fill in Firebase web config values")
    issues += 1

# ── 5. Python packages ────────────────────────────────────────────
print("\n[5] Python packages")
missing_pkgs = []
for pkg, import_name in [
    ("torch",          "torch"),
    ("transformers",   "transformers"),
    ("fastapi",        "fastapi"),
    ("firebase_admin", "firebase_admin"),
    ("uvicorn",        "uvicorn"),
    ("httpx",          "httpx"),
    ("dotenv",         "dotenv"),
]:
    try:
        __import__(import_name)
        check(pkg, True)
    except ImportError:
        check(pkg, False, f"pip install {pkg}")
        missing_pkgs.append(pkg)
        issues += 1

if missing_pkgs:
    print(f"\n  Run: pip install {' '.join(missing_pkgs)}")

# ── Summary ───────────────────────────────────────────────────────
print("\n=== Summary ==================================================")
if issues == 0:
    print(f"  {OK}  All checks passed! You can now run:")
    print("      Backend:  cd backend && uvicorn app.main:app --reload")
    print("      Frontend: cd frontend && npm run dev")
else:
    print(f"  {ERR} {issues} issue(s) found. Fix them above, then re-run this script.")
print()
sys.exit(0 if issues == 0 else 1)
