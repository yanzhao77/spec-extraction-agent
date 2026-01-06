"""
Test script to verify billing decisions for different scenarios.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.billing_decision import decide_billing

# Test Case 1: Successful extraction
print("=== Test Case 1: Successful Extraction ===")
result1 = decide_billing({"status": "completed", "validated_count": 10})
print(f"Billable: {result1['billable']}")
print(f"Reason: {result1['reason']}")
print(f"Expected: billable=True, reason=SUCCESSFUL_EXTRACTION")
print()

# Test Case 2: Empty document
print("=== Test Case 2: Empty Document ===")
result2 = decide_billing({"status": "completed", "validated_count": 0})
print(f"Billable: {result2['billable']}")
print(f"Reason: {result2['reason']}")
print(f"Expected: billable=False, reason=EMPTY_OR_INVALID_DOCUMENT")
print()

# Test Case 3: Partial success
print("=== Test Case 3: Partial Success ===")
result3 = decide_billing({"status": "completed_with_failures", "validated_count": 5})
print(f"Billable: {result3['billable']}")
print(f"Reason: {result3['reason']}")
print(f"Expected: billable=True, reason=PARTIAL_EXTRACTION_HIGH_CONFIDENCE")
print()

# Test Case 4: All validation failed
print("=== Test Case 4: All Validation Failed ===")
result4 = decide_billing({"status": "completed_with_failures", "validated_count": 0})
print(f"Billable: {result4['billable']}")
print(f"Reason: {result4['reason']}")
print(f"Expected: billable=False, reason=ALL_ITEMS_VALIDATION_FAILED")
print()

# Test Case 5: Agent execution failure
print("=== Test Case 5: Agent Execution Failure ===")
result5 = decide_billing({"status": "failed", "validated_count": 0})
print(f"Billable: {result5['billable']}")
print(f"Reason: {result5['reason']}")
print(f"Expected: billable=False, reason=AGENT_EXECUTION_FAILURE")
print()
