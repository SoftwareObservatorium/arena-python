import base64


def base64_encode(data):
    if isinstance(data, bytes):
        return base64.b64encode(data)
    elif isinstance(data, str):
        return base64.b64encode(data.encode()).decode()
    else:
        raise TypeError("Data must be bytes or string.")
