import ipaddress


def get_ip_version(ip_address: str) -> int | None:
    try:
        return ipaddress.ip_address(ip_address).version
    except ValueError:
        return None
