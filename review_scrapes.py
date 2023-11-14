import json
import os
from pathlib import Path
import csv

if __name__ == '__main__':
    for (root, dirs, files) in os.walk("_data/philadelphia_scraper/"):
        for f in files:
            obj = json.load(open(Path(root) / f,'r'))
            pass
