"""Entry-point shim so the launcher can start the Onboarding agent from the project root."""
import sys, os
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)                       # shared security module
sys.path.insert(0, os.path.join(ROOT, "onboarding"))
os.chdir(os.path.join(ROOT, "onboarding"))
import app
app.main()
