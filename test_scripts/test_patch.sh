#!/bin/bash

CALL_ID=$1

if [[ -z "$CALL_ID" ]]; then
  echo "Kullanım: $0 <call_id>"
  exit 1
fi

API_KEY="slsk6PYL"
ENDPOINT="http://aidata.com.tr/calls_test/$CALL_ID"

JSON=$(jq -n \
  --arg status "$2" \
  --arg doc_id "$3" \
  '{status: $status, doc_id: $doc_id}')

curl -s -X PATCH "$ENDPOINT" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$JSON" | jq
