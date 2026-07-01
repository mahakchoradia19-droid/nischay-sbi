"""Entry-point shim so the preview launcher can start SAARTHI from the project root."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "engage"))
os.chdir(os.path.join(os.path.dirname(__file__), "engage"))
import app
app.main()
