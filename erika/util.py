import math


def twos_complement_hex_string(number):
    """
    :param number: number to convert
    :return: the result as a hex string, e.g. "2A" for 42
    """
    intermediate = twos_complement(number)
    intermediate_bytes = intermediate.to_bytes(1, 'little')
    hex_string = intermediate_bytes.hex()
    return hex_string.upper()


def twos_complement(number):
    """
    "The two's complement of an N-bit number is defined as its complement with respect to 2^N.
    For instance, for the three-bit number 010, the two's complement is 110, because 010 + 110 = 1000.
    The two's complement is calculated by inverting the digits and adding one."

    https://en.wikipedia.org/wiki/Two%27s_complement
    """
    if (number < -128):
        raise Exception("Number out of range (low)")
    if (number > 127):
        raise Exception("Number out of range (high)")

    if (number < 0):
        all_ones = bytes.fromhex("FF")[0]
        number_in_positive = math.floor(math.fabs(number))
        bytes_of_number = number_in_positive.to_bytes(1, 'little')[0]
        xorResult = all_ones ^ bytes_of_number
        return xorResult + 1
    else:
        return number
