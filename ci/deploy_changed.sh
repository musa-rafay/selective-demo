#!/bin/bash
BED=$1          # e.g. testbed-alpha-bravo
LIST=$2         # csv list like "alpha,bravo"
IFS=',' read -ra ARR <<< "$LIST"
for svc in "${ARR[@]}"; do
  echo "Patching $svc in $BED"
  docker exec "$BED" sh -c "echo $svc > /root/$svc.tag"
done
