"""
Centralized Billing Decision Engine for the Spec Extraction Agent API.

All billing decisions MUST go through this module.
"""

from typing import Dict, Any

# --- Constants for Billing Reasons (Machine-Readable) ---
REASON_SUCCESS = "SUCCESSFUL_EXTRACTION"
REASON_PARTIAL_SUCCESS = "PARTIAL_EXTRACTION_HIGH_CONFIDENCE"
REASON_AGENT_FAILURE = "AGENT_EXECUTION_FAILURE"
REASON_VALIDATION_FAILURE = "ALL_ITEMS_VALIDATION_FAILED"
REASON_EMPTY_DOCUMENT = "EMPTY_OR_INVALID_DOCUMENT"


def decide_billing(agent_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determines if an agent execution is billable based on its final result.

    Args:
        agent_result: A dictionary containing the agent's execution summary.
                      Expected keys: 'status', 'validated_count', 'total_items'.

    Returns:
        A dictionary containing the billing decision.
        {
            "billable": bool,
            "reason": str (machine-readable reason),
            "unit": "per_call"
        }
    """
    status = agent_result.get("status", "AGENT_EXECUTION_FAILURE")
    validated_count = agent_result.get("validated_count", 0)

    # Default to non-billable
    billing_decision = {
        "billable": False,
        "reason": REASON_AGENT_FAILURE,
        "unit": "per_call"
    }

    if status == "completed":
        if validated_count > 0:
            # Case 1: Full success, at least one item extracted.
            billing_decision["billable"] = True
            billing_decision["reason"] = REASON_SUCCESS
        else:
            # Case 2: Agent ran successfully, but found nothing to extract.
            # This is considered a non-billable event as it provides no value.
            billing_decision["reason"] = REASON_EMPTY_DOCUMENT

    elif status == "completed_with_failures":
        if validated_count > 0:
            # Case 3: Partial success. Some items were extracted and validated.
            # This is considered billable as it provides partial value.
            billing_decision["billable"] = True
            billing_decision["reason"] = REASON_PARTIAL_SUCCESS
        else:
            # Case 4: Agent ran, but every single item failed validation.
            billing_decision["reason"] = REASON_VALIDATION_FAILURE

    # All other statuses (e.g., 'failed', 'error') will default to non-billable.

    return billing_decision
