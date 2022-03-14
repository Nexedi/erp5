"""Validates the transaction for both source and destination section.

XXX why proxy role ???
"""
transaction = state_change['object']

# Check constraints
transaction.Base_checkConsistency()
