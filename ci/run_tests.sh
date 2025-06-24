#!/bin/bash
SERVICES=$1
echo "Running smoke tests";  tests/smoke.sh
IFS=',' read -ra ARR <<< "$SERVICES"
for svc in "${ARR[@]}"; do
  tests/$svc.sh &
done
wait
