"""Vercel's FastAPI entrypoint; the same API is used locally."""
import ctypes
import os
import sys
from pathlib import Path

# Rasterio's Linux wheel expects Expat, absent from Vercel's runtime image.
if os.environ.get('VERCEL') == '1' and sys.platform == 'linux':
    ctypes.CDLL(str(Path(__file__).parent/'runtime_libs/libexpat.so.1'), mode=ctypes.RTLD_GLOBAL)

from backend.app import app
