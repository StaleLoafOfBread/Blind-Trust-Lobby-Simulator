# Blind Trust Lobby Simulator

Sends the lobby packet for game "[Blind Trust](https://store.steampowered.com/app/468560/Blind_Trust/)". Useful where broadcast packets are not routing such as when using [WireGuard VPN](https://www.wireguard.com/) to play over the internet.

## How to use

1. Start the lobby on Machine A
2. Run the script on Macine B: `python lobby.py --host_ip <ip of lobby>`
3. Inside the game click `join` on Machine B
4. Continue as normal

See help from script for more details: `python lobby.py --help`

## Troubleshooting

You may need to disable your VPN, run the script, click join, then enable your VPN. This is at least how it worked for WireGuard.

## Known limitations

- Does not send packets over the WireGuard interface. If anyone knows why, please let me know. You can still use it if you are using WireGuard, see [troubleshooting](#troubleshooting).
- When testing, the lobby as soldier worked as expected and allowed a game completion. Lobby as Oracle got to the pillar puzzle but the game would not recognize the Oracle completing their task. This could have been because the fake lobby was Solider but the real lobby was Oracle. Have not tested it with properly assigned character type fake lobby yet.
