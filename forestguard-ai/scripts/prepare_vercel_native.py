"""Copy the build image's Expat library into the Linux function bundle."""
import ctypes
import shutil
import sys
from pathlib import Path


def prepare(roots, output):
    candidates = [root/'libexpat.so.1' for root in roots]
    source = next((path.resolve() for path in candidates if path.is_file()), None)
    if source is None:
        raise RuntimeError('Build image lacks libexpat.so.1; cannot package Rasterio runtime.')
    output.mkdir(parents=True, exist_ok=True)
    target = output/'libexpat.so.1'
    shutil.copyfile(source, target)
    return target


if __name__ == '__main__':
    if sys.platform != 'linux':
        raise RuntimeError('Run this packaging step in the Vercel Linux build, not on Windows.')
    roots = [Path(value) for value in ('/lib64', '/usr/lib64', '/lib', '/usr/lib',
        '/lib/x86_64-linux-gnu', '/usr/lib/x86_64-linux-gnu',
        '/lib/aarch64-linux-gnu', '/usr/lib/aarch64-linux-gnu')]
    target = prepare(roots, Path(__file__).resolve().parents[1]/'runtime_libs')
    ctypes.CDLL(str(target), mode=ctypes.RTLD_GLOBAL)
    print('Bundled and loaded libexpat.so.1 ('+str(target.stat().st_size)+' bytes).')
