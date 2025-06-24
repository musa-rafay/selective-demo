#!/usr/bin/env python3
import yaml
with open('stable-builds.yml','w') as f:
    yaml.dump({'alpha':'alpha:1.0','bravo':'bravo:1.0'}, f)
print('stable-builds.yml written')
