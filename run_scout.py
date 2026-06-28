"""Entry-point shim so the preview launcher can start scout from the project root."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scout"))
os.chdir(os.path.join(os.path.dirname(__file__), "scout"))
import app
app.main()
