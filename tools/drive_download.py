#!/usr/bin/env python3
"""Download a public ("anyone with the link") Drive folder or file into work/<name>/raw/."""
import argparse
import pathlib
import sys

import gdown

ap = argparse.ArgumentParser()
ap.add_argument('url')
ap.add_argument('--name', required=True, help='batch name, becomes work/<name>/raw')
a = ap.parse_args()
dest = pathlib.Path('work') / a.name / 'raw'
dest.mkdir(parents=True, exist_ok=True)
if '/folders/' in a.url:
    files = gdown.download_folder(url=a.url, output=str(dest), quiet=False, remaining_ok=True)
else:
    files = [gdown.download(url=a.url, output=str(dest) + '/', quiet=False)]
if not files or not all(files):
    sys.exit('Download failed or incomplete. Is the link shared as "Anyone with the link"?')
for f in files:
    print(f)
