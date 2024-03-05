def map_value(x, in_min, in_max, out_min, out_max):
    """
    Maps a value x from one range [in_min, in_max] to another [out_min, out_max].

    Parameters:
    - x: The value to map.
    - in_min: The lower bound of the input range.
    - in_max: The upper bound of the input range.
    - out_min: The lower bound of the output range.
    - out_max: The upper bound of the output range.

    Returns:
    - The value mapped to the new range.
    """
    # First, subtract the minimum of the input range to translate x to start from 0,
    # then scale the value to the proportion it represents in the input range.
    # Finally, scale this proportion to the output range and translate it to start from out_min.
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
