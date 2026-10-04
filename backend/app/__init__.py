"""GIFT Setup Navigator backend application package."""
from pathlib import Path

from dotenv import load_dotenv

# Local secrets/config live in backend/.env (gitignored). Real environment
# variables (e.g. set in the Render dashboard) take precedence over the file.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
