import subprocess

# find broadcast address
broadcast = (
    subprocess.check_output("ifconfig | grep broadcast | awk '{print $6}'", shell=True)
    .decode()
    .strip()
)
print(f"Broadcast address: {broadcast}")
# ping broadcast address
subprocess.run(["ping", "-c", "1", broadcast])

# scan local network
arp = subprocess.Popen(["arp", "-a"], stdout=subprocess.PIPE)
grep = subprocess.Popen(
    ["grep", "-v", "'incomplete'"], stdin=arp.stdout, stdout=subprocess.PIPE
)
tr = subprocess.Popen(["tr", "-d", "'()'"], stdin=grep.stdout, stdout=subprocess.PIPE)
output = subprocess.check_output(["awk", "{print $2, $4}"], stdin=tr.stdout)
devices = output.decode().strip().splitlines()
devices = [device.split() for device in devices]

# scan open ports
devices_ports = {}
for device in devices:
    try:
        print(f"IP: {device[0]}, MAC: {device[1]}")
        nmap = subprocess.Popen(["nmap", "-Pn", device[0]], stdout=subprocess.PIPE)
        output = (
            subprocess.check_output(["grep", "open"], stdin=nmap.stdout)
            .decode()
            .strip()
        )
        ports = [
            (tmp[0], tmp[1]) for port in output.splitlines() if (tmp := port.split())
        ]
        devices_ports.update({device[0]: ports})
    except KeyboardInterrupt as e:
        break

print(devices_ports)
