import argparse
from ipaddress import IPv4Address, ip_address
import time
from scapy.all import *


# What interface should we send this on
# You can use `conf.ifaces` to list the available interfaces
IFACE = conf.iface
# IFACE = conf.ifaces.dev_from_index(1)  # loopback
# IFACE = conf.ifaces.dev_from_name("WireGuard Tunnel")
# IFACE = conf.ifaces.dev_from_name("Intel(R) I211 Gigabit Network Connection")

# What port is the lobby being hosted on
BLIND_TRUST_LOBBY_HOST_PORT = 47777


class CharacterType:
    Oracle = "Oracle"
    Soldier = "Soldier"

    def __init__(self, character_type_str):
        if character_type_str == self.Oracle or character_type_str == self.Soldier:
            self.character_type = character_type_str
        else:
            raise ValueError("Invalid character type")

    def __str__(self):
        return self.character_type


def string_to_byte_string_with_nulls(input_string):
    byte_string_with_nulls = b"\x00".join(ord(char).to_bytes(1, byteorder="big") for char in input_string)
    return byte_string_with_nulls


def generate_lobby_load(character: CharacterType, name: str) -> bytes:
    """
    Can be used directly like:

    load = generate_lobby_load(character, name)
    UDP(dport=47777, sport=54321) / load
    """

    soldier = b"\xd4B"
    oracle = b"\xc7j"

    prefix = b"\x00\x00\t"
    characterIndicator = soldier if character is CharacterType.Soldier else oracle
    padding = b"\x00\x00\x08\xae\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01"
    lobby = string_to_byte_string_with_nulls(name)
    splitter = b"\x00"
    charName = string_to_byte_string_with_nulls(f":{str(character)}")
    end = b"\x00"

    return b"".join([prefix, characterIndicator, padding, lobby, splitter, charName, end])


def send_lobby(
    host_ip: ip_address,
    joiner_ip: ip_address = IPv4Address("255.255.255.255"),
    character: CharacterType = CharacterType.Soldier,
    name: string = None,
    count: int = 50,
    secs_between_resends: float = 0.5,
    host_port: int = 54321,
):
    if name is None:
        name = f"Magic Lobby {host_ip} -> {joiner_ip}"

    load = generate_lobby_load(character, name)

    print(f"Starting {character} lobby [{name}]")
    print(f"Host: {host_ip}")
    print(f"Joiner: {joiner_ip}")

    for i in range(0, count):
        udp_packet = UDP(dport=BLIND_TRUST_LOBBY_HOST_PORT, sport=host_port) / load
        ip_packet = IP(dst=str(joiner_ip), src=str(host_ip))
        p = ip_packet / udp_packet
        send(p, iface=IFACE)
        time.sleep(secs_between_resends)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
Script to send lobby packets for Blind Trust. This is useful to trick the game into "seeing" the lobby when broadcast packets are not routing.
"""
    )
    parser.add_argument(
        "--host_ip",
        type=ip_address,
        default=get_if_addr(IFACE),
        help="IP of the machine hosting the lobby. Defaults to the IP of the machine running the script.",
    )
    parser.add_argument(
        "--joiner_ip",
        type=ip_address,
        default=get_if_addr(IFACE),
        help="IP of the machine you wish to join the Lobby. Defaults to the IP of the machine running the script.",
    )
    parser.add_argument(
        "--character",
        type=str,
        default="Soldier",
        help="What character is the lobby host playing as. Can be `Soldier` or `Oracle`",
    )
    parser.add_argument(
        "--lobby_name",
        type=str,
        default=None,
        help="What to call the lobby",
    )
    args = parser.parse_args()

    print(IFACE.name)
    send_lobby(
        host_ip=args.host_ip, joiner_ip=args.joiner_ip, character=CharacterType(args.character), name=args.lobby_name
    )
