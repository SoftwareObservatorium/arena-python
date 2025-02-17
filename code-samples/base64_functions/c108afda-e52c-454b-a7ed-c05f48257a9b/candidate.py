def base64_encode(data):
    if not isinstance(data, str):
        raise TypeError("Input must be a string.")

    # Define Base64 algorithm steps
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/'
    index_chars = {char: i for i, char in enumerate(chars)}

    def encode_bin(bin_data):
        return bin_data.replace('0b', '').replace("'", "")

    encoded_bytes = b''
    while len(data) > 0:
        chunk_size = min(3, len(data))
        chunk = data[:chunk_size]
        remaining = data[chunk_size:]

        # Convert chunk to binary
        bin_ = encode_bin(str(chunk)[2:])

        # Find index for each character in the binary string
        indexes = []
        for char in bin_:
            indexes.append(index_chars[char])
        encoded_bytes += bytes([i % 6 + (indexes[i] >> 2) + (indexes[i] & 0b001) << 4 for i in range(len(bin_))])

        # Add padding if necessary
        if len(bin_) % 3 != 0:
            pad = '=' * ((3 - len(bin_) % 3) % 3)
            encoded_bytes += bytes([ord(pad)])
            data = remaining

    return encoded_bytes.decode() + "=" * (3 - len(encoded_bytes) % 3)

