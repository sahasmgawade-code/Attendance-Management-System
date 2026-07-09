import ipaddress

from config.config import Config


def get_client_ip(request):
    # If ever placed behind a reverse proxy, the real client IP
    # comes first in X-Forwarded-For. For direct local access
    # (no proxy), request.remote_addr is correct.
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr


def is_ip_allowed(ip_str):
    settings = Config.load_settings()
    allowed_networks = settings.get("checkin_allowed_networks", [])

    if not allowed_networks:
        return False

    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False

    for network_str in allowed_networks:
        try:
            network = ipaddress.ip_network(network_str, strict=False)
            if ip in network:
                return True
        except ValueError:
            continue

    return False