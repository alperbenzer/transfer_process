#!/bin/bash

if [ ! -z $1 ]
then

curl -s -X PATCH http://localhost:8000/calls/$1 \
  -H "X-API-KEY: slsk6PYL" \
  -H "Content-Type: application/json" \
  -d '{
        "status": "İNCELEMEDE",
        "doc_id": "DOC-001"
      }' | jq

fi