#!/bin/bash

# Generate a random external_call_id
external_call_id="TEST-$(date +%s%N | sha256sum | head -c 8)"

curl -s -X POST http://aidata.com.tr/transfer \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: PHFVNOY9" \
  -d '{
    "external_call_id": "'"$external_call_id"'",
    "call_date": "2025-05-01T14:30:00",
    "serial_number": "XYZ12345",
    "title": "Test Arızası",
    "subject": "Deneme",
    "description": "Bu bir test çağrısıdır.",
    "address": "Test Mahallesi No:42",
    "school_code": "999999",
    "school_name": "Test Okulu",
    "province": "Testcity",
    "district": "Testtown",
    "reporter_name": "Alper Test",
    "phone": "5000000000",
    "email": "alper@test.com",
    "product_type": "MPC1"
}' | jq
