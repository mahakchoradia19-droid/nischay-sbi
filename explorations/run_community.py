"""Entry-point shim so the launcher can start the DBT Gap Agent from the project root."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "community"))
os.chdir(os.path.join(os.path.dirname(__file__), "community"))
import app
app.main()
