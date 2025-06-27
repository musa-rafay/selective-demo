#!/usr/bin/env python3
import yaml
import os

def bump(version):
    parts = version.split('.')
    if len(parts) == 2 and all(p.isdigit() for p in parts):
        major, minor = map(int, parts)
        return f"{major}.{minor + 1}"
    else:
        return '1.0'  # fallback

filename = 'stable-builds.yml'

# Load existing versions or start fresh
if os.path.exists(filename):
    with open(filename) as f:
        builds = yaml.safe_load(f) or {}
else:
    builds = {}

# Only store versions like "1.0", not "alpha:1.0"
builds['alpha'] = bump(str(builds.get('alpha', '1.0')))
builds['bravo'] = bump(str(builds.get('bravo', '1.0')))

with open(filename, 'w') as f:
    yaml.dump(builds, f)

print("stable-builds.yml updated:", builds)
