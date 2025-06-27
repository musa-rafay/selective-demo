#!/usr/bin/env python3
import yaml
import os

def bump(version):
    major, minor = map(int, version.split('.'))
    return f"{major}.{minor + 1}"

filename = 'stable-builds.yml'

# Load existing versions or start fresh
if os.path.exists(filename):
    with open(filename) as f:
        builds = yaml.safe_load(f) or {}
else:
    builds = {}

# Default to 1.0 if not set, otherwise bump
builds['alpha'] = bump(builds.get('alpha', '1.0'))
builds['bravo'] = bump(builds.get('bravo', '1.0'))

# Save updated versions
with open(filename, 'w') as f:
    yaml.dump(builds, f)

print("stable-builds.yml updated:", builds)
