#!/usr/bin/env python3
# Adrian Vollmer, SySS GmbH 2016

"""
Usage: alternate-dns.py -h
"""


import socket
import dnslib
import argparse
import re
import os


parser = argparse.ArgumentParser(
    description="A fake DNS server to easily MitM devices that you control"
)
parser.add_argument('-p', '--port', default=53, dest="PORT", type=int,
    help="the UDP port to listen on (default: 53)")
parser.add_argument('-b', '--bind-address', default='',
    dest="BIND_ADDRESS", type=str,
    help="the bind address to listen on (default: '')")
parser.add_argument('-f', '--file', default='', dest="HOSTS_FILE", type=str,
    help="path to a custom hosts file")
parser.add_argument('-d', '--dns-server', default='', dest="DNS_SERVER", type=str,
    help="address of the default DNS server (leave empty for DNS of the system)")
parser.add_argument('HOST', type=str, default=[], action="store", nargs='*',
    help="a comma separated value pair specifying the hostname " +
        "(as a regular expression) and the IP address " +
        "(example: .*example.org,127.0.0.1)"
    )
#  parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')
args = parser.parse_args()

HOSTS_LIST = []


def fill_hosts_list():
    global HOSTS_LIST
    if args.HOST == [] and args.HOSTS_FILE == "":
        print("Warning: No hosts specified. Operating in passive mode.")

    if not args.HOST == []:
        HOSTS_LIST += [x.split(',') for x in args.HOST]

    if not args.HOSTS_FILE == "":
        with open(args.HOSTS_FILE, 'r') as f:
            hosts = f.readlines()
        for line in hosts:
            line = re.sub(r'#.*$', '', line)
            line = re.sub(r'\s+', ' ', line.strip())
            HOSTS_LIST += [line.split(' ')]


def receiveData(udps):
    types = {1: "A", 2: "NS", 15: "MX", 16: "TXT", 28: "AAAA"}
    data, addr = udps.recvfrom(1024)
    dnsD = dnslib.DNSRecord.parse(data)
    try:
        type = types[dnsD.questions[0].qtype]
    except KeyError:
        type = "OTHER"
    labels = dnsD.questions[0].qname.label
    answer = dnsD.reply()
    domain = b'.'.join(labels)
    domain = domain.decode()
    print("%s:%d is requesting the %s record of %s" %
        (addr[0], addr[1], type, domain))
    return data, addr, type, domain, answer


def sendData(udps, addr, answer):
    udps.sendto(answer.pack(), addr)

# The TLS CRLF injection changes start here

spoof_count = 0

def get_spoofed_IP(domain):
    global spoof_count
    for d in HOSTS_LIST:
        if re.match(d[0], domain):
            spoof_count = (spoof_count + 1) % 2
            return d[1] if spoof_count else '127.0.0.1'
    return None

# end

def get_dns_ip():
    if args.DNS_SERVER == "":
        with open('/etc/resolv.conf', 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line.startswith("nameserver"):
                    _ , ip = line.split()
                    return ip
    else:
        return args.DNS_SERVER

    print("Couldn't determine the system's DNS server")
    exit(1)


def forwarded_dns_request(data):
    DNS_IP = get_dns_ip()

    print("Forwarding DNS request to " + DNS_IP)
    udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udps.sendto(data, (DNS_IP, 53))
    data, addr = udps.recvfrom(1024)

    return data


def spoofed_answer(answer, domain, IP):
    answer.add_answer(
        *dnslib.RR.fromZone('%s 0 %s %s' % (
            domain,
            "A",
            IP)
        ))
    return answer


def main_loop(udps):
    while True:
        data, addr, type, domain, answer = receiveData(udps)
        ip = get_spoofed_IP(domain)
        if type == "A" and ip:
            print("Answering with %s" % ip)
            answer = spoofed_answer(answer, domain, ip)
            sendData(udps, addr, answer)
        else:
            answer = forwarded_dns_request(data)
            udps.sendto(answer, addr)


def drop_privileges():
    try:
        uid = int(os.environ['SUDO_UID'])
        if uid > 0:
            print("Dropping privileges to UID %d" % uid)
            os.setuid(uid)
    except:
        print("Warning: Failed to drop privileges")


def init_listener():
    try:
        udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udps.bind((args.BIND_ADDRESS, args.PORT))
    except PermissionError:
        print("This script must be run as root if you want to listen " +
            "on port %d" % args.PORT)
        exit(1)
    return udps


def main():
    print("DNS MitM by Adrian Vollmer, SySS GmbH")

    udps = init_listener()
    drop_privileges()
    fill_hosts_list()
    try:
        main_loop(udps)
    except KeyboardInterrupt:
        exit(0)


if __name__ == '__main__':
    main()