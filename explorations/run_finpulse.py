"""Entry-point shim so the preview launcher can start FinPulse from the project root."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "finpulse"))
os.chdir(os.path.join(os.path.dirname(__file__), "finpulse"))
import app
app.main()
