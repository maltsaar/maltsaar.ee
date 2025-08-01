---
title = "Routing Firefox traffic through Wireguard"
description = "How I got Wireguard working in an isolated network namespace using wg-quick, microsocks and socat"
published = "2025-08-01T15:16Z"
---

I wanted a setup where I can open my browser and have my traffic automatically routed through a VPN without messing with the rest of my system.

What came to me as a big surprise is that achieving this is actually somewhat complicated. There is no browser extension that just does this for you.

With the help of AI and some troubleshooting this is what I ended up coming up with.

## The core script

Here's a breakdown of the core script `wg_browser_ns.sh`:

```shell
#!/bin/bash

NETWORK_INTERFACE=eth0
VPN_DNS_SERVER=X.X.X.X

# Clean up old setup
ip netns delete vpn-ns 2>/dev/null || true
ip link delete veth-host 2>/dev/null || true
pkill -f microsocks 2>/dev/null || true
pkill -f "socat TCP-LISTEN:1080" 2>/dev/null || true

# Create network namespace
ip netns add vpn-ns

# Create veth pair
ip link add name veth-host type veth peer name veth-ns
ip link set veth-ns netns vpn-ns

# Set up host-side veth
ip addr add 10.200.200.1/24 dev veth-host
ip link set veth-host up

# Set up namespace-side veth
ip netns exec vpn-ns ip addr add 10.200.200.2/24 dev veth-ns
ip netns exec vpn-ns ip link set veth-ns up
ip netns exec vpn-ns ip link set lo up

# Default route inside namespace
ip netns exec vpn-ns ip route add default via 10.200.200.1

# Setup DNS inside namespace
ip netns exec vpn-ns bash -c 'echo "nameserver $VPN_DNS_SERVER" > /etc/resolv.conf'

# Enable NAT and IP forwarding
iptables -t nat -C POSTROUTING -s 10.200.200.0/24 -o $NETWORK_INTEFACE -j MASQUERADE 2>/dev/null || \
iptables -t nat -A POSTROUTING -s 10.200.200.0/24 -o $NETWORK_INTERFACE -j MASQUERADE

# Allow forwarding from your veth subnet to the external interface
iptables -A FORWARD -i veth-host -o $NETWORK_INTERFACE -j ACCEPT

# Allow forwarding for established/related connections back from $NETWORK_INTERFACE to veth-host
iptables -A FORWARD -i $NETWORK_INTERFACE -o veth-host -m state --state RELATED,ESTABLISHED -j ACCEPT

sysctl -w net.ipv4.ip_forward=1

# Bring up WireGuard interface via wg-quick inside the namespace
ip netns exec vpn-ns wg-quick up /etc/wireguard/no-osl-wg-001.conf

# Start microsocks inside the namespace on 127.0.0.1:1081
ip netns exec vpn-ns microsocks -i 127.0.0.1 -p 1081 &

# Forward proxy port from namespace to host
socat TCP-LISTEN:1080,fork,reuseaddr EXEC:/usr/local/bin/forward-socks-traffic
```

## Making it so Firefox can connect to the proxy

A little trick is used in `wg_browser_ns.sh` so Firefox can access the socks proxy. We forward traffic from the host into the namespace via socat:

```shell
socat TCP-LISTEN:1080,fork,reuseaddr EXEC:/usr/local/bin/forward-socks-traffic
```

The proxy script `forward-socks-traffic` looks like this:
```shell
#!/bin/bash
exec ip netns exec vpn-ns socat STDIO TCP4:127.0.0.1:1081
```

## Setting up wireguard configuration

`/etc/wireguard/wireguard.conf` in this example is just a standard wireguard configuration file.

Under `[Interface]` you need to add the following `PostUp` and `PostDown` parameters:
```ini
PostUp = cp /etc/resolv.conf.wgbackup /etc/resolv.conf
PostDown = cp /etc/resolv.conf.wgbackup /etc/resolv.conf
```

This is done because wg-quick overwrites the systems `/etc/resolv.conf` file which we want to avoid.

After this make a copy of your current resolv.conf file:
```shell
cp /etc/resolv.conf /etc/resolv.conf.wgbackup
```

## Creating the systemd service

I have the following systemd unit in `/etc/systemd/system/wg-browser-ns.service`:

```ini
[Unit]
Description=WireGuard VPN Namespace Setup with SOCKS Proxy
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/local/bin/wg_browser_ns.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Lets make sure the service is enabled on startup and currently running:
```shell
systemctl daemon-reload
systemctl enable wg-browser-ns.service
systemctl start wg-browser-ns.service
```

## Configuring socks proxy in firefox

In Firefox it's as simple as just navigating to Settings -> Network Settings and setting your proxy settings as follows:

![Firefox network settings](/assets/images/firefox-network-settings.png)