# puprisa/utils/range_parser_utils.py

def parse_range_string(input_str: str, offset: int = 0) -> list[int]:
    """Parse a range string like "1,3-5" into a list of zero-based indices.

    Args:
        input_str: The user-supplied string, e.g. "1,3-5".
        offset: Page-base offset. Pass -1 to convert 1-based page
            numbers to 0-based indices. Defaults to 0, meaning the
            parsed numbers are returned unchanged.

    Returns:
        A sorted, de-duplicated list of integers. For example,
        "1,3-5" with offset=-1 returns [0, 2, 3, 4].

    Raises:
        ValueError: If a token contains more than one '-', or if any
            token cannot be parsed as an integer.
    """
    pages = []
    tokens = [t.strip() for t in input_str.split(',') if t.strip()]
    for token in tokens:
        if '-' in token:
            parts = token.split('-')
            if len(parts) != 2:
                raise ValueError(f"Invalid range: {token}")
            start, end = map(int, parts)
            if start > end:
                start, end = end, start
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(token))
    pages = sorted(set(pages))
    return [p + offset for p in pages]