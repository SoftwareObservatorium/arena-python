class Base64:

    def base64_encode(self, data):
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/'
        index_chars = {char: i for i, char in enumerate(chars)}

        def encode_bin(bin_data):
            return bin_data.replace('0b', '').replace("'", "")

        encoded_bytes = b''
        data_copy = list(data)
        while len(data_copy) > 0:
            chunk_size = min(3, len(data_copy))
            chunk = data_copy[:chunk_size]
            remaining = data_copy[chunk_size:]

            bin_str = encode_bin(str(chunk)[2:])
            indexes = [index_chars[char] for char in bin_str]

            encoded_bytes += bytes([i % 6 + (indexes[i] >> 2) + (indexes[i] & 0b001) << 4 for i in range(len(bin_str))])

            if len(bin_str) % 3 != 0:
                pad = '=' * ((3 - len(bin_str) % 3) % 3)
                encoded_bytes += bytes([ord(pad)])
                data_copy = remaining
        return (encoded_bytes.decode() + "=" * (3 - len(encoded_bytes) % 3))

