def generate_number(prefix: str, sequence: int) -> str:
    """Human-readable business ID, e.g. REQ-1000, ORD-1000.

    Count-based sequence — has a narrow race-condition window under
    concurrent writes (acceptable for assessment scope; the unique
    constraint on the column guarantees a collision fails loudly with
    IntegrityError rather than silently overwriting data). A DB sequence
    would close this gap in a production system.
    """
    return f"{prefix}-{1000 + sequence}"