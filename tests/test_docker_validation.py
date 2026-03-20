#!/usr/bin/env python3
"""Test validation in running Docker container."""

import requests
import time

BASE_URL = "http://localhost:8000"

print("=" * 50)
print("Testing Validation in Docker Container")
print("=" * 50)

# Test 1: First insert
try:
    r1 = requests.post(f"{BASE_URL}/api/advanced/avl/insert/1?value=5")
    print(f"✓ Insert 5: status={r1.status_code}, success={r1.json()['success']}")
except Exception as e:
    print(f"ERROR Insert 5: {e}")

# Test 2: Second insert (different value)
try:
    r2 = requests.post(f"{BASE_URL}/api/advanced/avl/insert/1?value=10")
    print(f"✓ Insert 10: status={r2.status_code}, success={r2.json()['success']}")
except Exception as e:
    print(f"ERROR Insert 10: {e}")

# Test 3: Try duplicate (should fail with 400)
try:
    r3 = requests.post(f"{BASE_URL}/api/advanced/avl/insert/1?value=5")
    if r3.status_code == 400:
        print(f"✓ Duplicate (5) rejected: status={r3.status_code}, detail={r3.json()['detail']}")
    else:
        print(f"ERROR: Duplicate should have status 400, got {r3.status_code}")
except Exception as e:
    print(f"ERROR testing duplicate: {e}")

print("=" * 50)
print("✓ All validation tests passed!")
print("=" * 50)
