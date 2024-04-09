def condense_to_ranges(integers):
    ranges = []
    start = None
    prev = None

    for num in sorted(integers):
        if start is None:
            start = num
            prev = num
        elif num == prev + 1:
            prev = num
        else:
            ranges.append(f"{start}-{prev}")
            start = num
            prev = num
    
    # Add the last range
    if start is not None:
        ranges.append(f"{start}-{prev}")

    return ranges