"""
Rebuild content for the switcher.json file, write to stdout
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path().absolute().parent.parent))
import pysumreg

BASE_URL = "https://prjemian.github.io/pysumreg"
version = pysumreg.__version__

# TODO: this could be input args
# First one will be marked as "latest".
releases = """
    1.0.4
    1.0.3
    1.0.1
    1.0.0
""".split()

switcher = [dict(version=r, url=f"{BASE_URL}/{r}") for r in releases]
switcher[0]["name"] = f"{releases[0]} (latest)"

if ".dev" in version:
    switcher.insert(
        0,
        dict(
            name=f"{version} (development)",
            version="dev",
            url=f"{BASE_URL}/{version}"
        )
    )

# TODO: Make certain that _some_ "dev" is designated.

print(json.dumps(switcher, indent=4))
