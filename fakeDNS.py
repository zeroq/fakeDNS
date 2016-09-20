# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

import sys, socket, argparse
from dnslib import DNSRecord, DNSHeader, RR, A, QTYPE

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process input')
    parser.add_argument("--ip", help="set listen ip address", action="store", type=str, default="192.168.57.1")
    parser.add_argument("--port", help="set listen port", action="store", type=int, default=53)
    parser.add_argument("--withInternet", help="enable real resolving", action="store_true")
    parser.add_argument("--debug", help="enable debug logging", action="store_true")
    args = parser.parse_args()

    if args.debug:
        print('IP: %s Port: %s withInternet: %s' % (args.ip, args.port, args.withInternet))

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind((args.ip, args.port))

    try:
        while True:
            data, addr = udp_sock.recvfrom(1024)
            d = DNSRecord.parse(data)
            for question in d.questions:
                qdom = question.get_qname()
                r = d.reply()
                if args.withInternet:
                    try:
                        realip = socket.gethostbyname(qdom.idna())
                    except Exception as e:
                        if args.debug:
                            print(e)
                        realip = args.ip
                    r.add_answer(RR(qdom,rdata=A(realip),ttl=60))
                    if args.debug:
                        print("Request: %s --> %s" % (qdom.idna(), realip))
                else:
                    r.add_answer(RR(qdom,rdata=A(args.ip),ttl=60))
                    if args.debug:
                        print("Request: %s --> %s" % (qdom.idna(), args.ip))
                udp_sock.sendto(r.pack(), addr)
    except KeyboardInterrupt:
        if args.debug:
            print("done.")
    udp_sock.close()
