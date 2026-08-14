"""
Run this first on any new device:
    python check_setup.py
"""
import sys, os

results = []

def check(name, fn):
    try:
        fn()
        results.append(("✅", name, "OK"))
    except ImportError:
        results.append(("❌", name, f"NOT INSTALLED — pip install {name.lower().replace(' ','-')}"))
    except Exception as e:
        results.append(("⚠️", name, f"Installed but error: {e}"))

check("streamlit",     lambda: __import__("streamlit"))
check("groq",          lambda: __import__("groq"))
check("chromadb",      lambda: __import__("chromadb"))
check("pypdf",         lambda: __import__("pypdf"))
check("python-docx",   lambda: __import__("docx"))
check("python-pptx",   lambda: __import__("pptx"))
check("python-dotenv", lambda: __import__("dotenv"))
check("lxml",          lambda: __import__("lxml"))
check("Pillow",        lambda: __import__("PIL"))

# SQLite (built-in)
check("sqlite3",       lambda: __import__("sqlite3"))

# .env check
env_ok = os.path.exists(".env")
if env_ok:
    with open(".env") as f:
        content = f.read()
    key = next((l.split("=",1)[1].strip() for l in content.splitlines() if l.startswith("GROQ_API_KEY=")), "")
    if key and key != "your_groq_api_key_here":
        results.append(("✅", ".env / GROQ_API_KEY", "Key found"))
    else:
        results.append(("❌", ".env / GROQ_API_KEY", "Key missing — add from console.groq.com"))
else:
    results.append(("❌", ".env file", "Not found — create it with GROQ_API_KEY=your_key"))

results.append(("✅" if os.path.exists("assets/SBBWUP_logo.png") else "❌",
                "assets/SBBWUP_logo.png",
                "Found" if os.path.exists("assets/SBBWUP_logo.png") else "Missing"))

print("\n" + "="*58)
print("   AGENTIC AI STUDY HELPER — Setup Check")
print("="*58)
for icon, name, status in results:
    print(f"  {icon}  {name:<25} {status}")
print("="*58)

errors = [r for r in results if r[0] == "❌"]
if errors:
    print(f"\n  ⚠️  {len(errors)} issue(s) found. Fix them then run again.\n")
    sys.exit(1)
else:
    print("\n  🎉 All good! Run: streamlit run app.py\n")
