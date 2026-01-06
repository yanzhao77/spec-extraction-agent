#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
One-Click Example Runner for the Engineering Specification Extraction Agent.

This script demonstrates the agent's full lifecycle, including the self-repair mechanism.
It processes a sample document, prints the final JSON output, and highlights key
log entries that show the agent's state transitions.

Usage:
    python examples/run_example.py [--document /path/to/your/document.txt]
"""

import os
import sys
import argparse
import logging

# Add the src directory to the Python path to allow importing the agent
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agent import ExtractionAgentFinal
os.environ["OPENAI_API_KEY"] = "2cb6d2e323ed4f3badc136090daa0ccb.87GF3FfJmNUuQcSd"

def main():
    """Main function to run the agent and display results."""
    parser = argparse.ArgumentParser(description="Run the Engineering Specification Extraction Agent.")
    parser.add_argument(
        '--document',
        type=str,
        default=os.path.join(os.path.dirname(__file__), 'GB50016_2014_sample.txt'),
        help='Path to the document to be processed.'
    )
    args = parser.parse_args()

    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ ERROR: OPENAI_API_KEY environment variable not set.")
        print("Please set it before running: export OPENAI_API_KEY=\"your_api_key_here\"")
        sys.exit(1)

    print("🚀 Starting Engineering Specification Extraction Agent...")
    print(f"Processing document: {args.document}")
    print("--- " * 20)

    # --- Run the Agent ---
    agent = ExtractionAgentFinal(document_path=args.document)
    final_json_output = agent.run()

    # --- Display Results ---
    print("\n" + "--- " * 20)
    print("✅ AGENT EXECUTION FINISHED")
    print("--- " * 20)

    print("\n📋 FINAL EXTRACTED JSON OUTPUT:")
    print(final_json_output)

    # --- Highlight Key Log Events ---
    print("\n" + "--- " * 20)
    print("🔍 HIGHLIGHTS FROM THE EXECUTION LOG:")
    print("This shows the agent's self-repair process.")
    print("--- " * 20)

    log_file = 'agent_mvp_final.log'
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            found_validation = False
            found_repair = False
            for line in f:
                if "STATE TRANSITION: EXTRACTION -> VALIDATION" in line:
                    found_validation = True
                if "STATE TRANSITION: VALIDATION -> REPAIR" in line:
                    found_repair = True
                
                if found_validation and "failed validation" in line:
                    print(f"   [FAILED] {line.strip()}")
                if found_repair and "Attempting to repair" in line:
                    print(f"   [REPAIRING] {line.strip()}")
                if found_repair and "STATE TRANSITION: REPAIR -> VALIDATION" in line:
                    print(f"   [REPAIRED] {line.strip()}")

    print("\nFull execution trace is available in 'agent_mvp_final.log'")

if __name__ == "__main__":
    main()
