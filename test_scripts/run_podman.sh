#!/bin/bash

podman run -p 8000:8000 \
  --env-file=.env \
  -v $(pwd)/aidata.db:/app/aidata.db \
  transfer_process

