from jc_sre_netprobe import network_info


def test_ipv4_network_info() -> None:
    result = network_info("192.168.10.50/24")

    assert result.network == "192.168.10.0"
    assert result.prefix_length == 24
    assert result.netmask == "255.255.255.0"
    assert result.broadcast == "192.168.10.255"
    assert result.total_addresses == 256
    assert result.ip_version == 4
    assert result.is_private is True


def test_ipv6_network_info() -> None:
    result = network_info("2001:db8::10/64")

    assert result.network == "2001:db8::"
    assert result.prefix_length == 64
    assert result.ip_version == 6
    assert result.broadcast is None
