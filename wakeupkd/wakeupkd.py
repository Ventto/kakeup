#!/usr/bin/env python
#
# MIT License
#
# Copyright (c) 2016 Thomas "Ventto" Venriès
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os
import signal
import socket
import sys
import struct

WOLH_PASSWD_NONE     = 102
WOL_PACKET_MIN_BYTES = 130
WOL_PACKET_MAX_BYTES = 176
DEFAULT_PORT         = 9
DEFAULT_HOST         = "0.0.0.0"

def __get_size(obj, seen=None):
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum((get_size(v, seen) for v in obj.values()))
        size += sum((get_size(k, seen) for k in obj.keys()))
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum((get_size(i, seen) for i in obj))
    return size

def __ip_ipsrccheck(ipsrc, data):
    ipsrc_s = ipsrc.split('.')
    ipsrc_b = [int(i) for i in ipsrc_s]
    for i in range(4):
        print (data[i], ';', ipsrc_b[i])
        if data[i] != ipsrc_b[i]:
            return False
    return True

def __wol_datacheck(macaddr, data):
    mac_bytes = bytearray.fromhex(macaddr.replace(':', ''))
    for i in range(6):
        if data[i] != 0xFF:
            return False
    j = 0
    for i in range(6, 102):
        if data[i] != mac_bytes[j]:
            return False
        j = (j + 1) % 6
    return True

def __wol_pktcheck(packet, macaddr = None, ipsrc = None):
    size = __get_size(packet)
    if size < WOL_PACKET_MIN_BYTES:
        return False

    iph         = struct.unpack('!BBHHHBBH4s4s' , packet[0:20])
    iph_version = iph[0] >> 4
    iph_len     = (iph[0] & 0xF) * 4
    iph_ipsrc   = iph[8]

    if ipsrc != None and not __ip_ipsrccheck(ipsrc, iph_ipsrc):
        return False

    udph        = struct.unpack('!4H' , packet[iph_len: iph_len + 8])
    udph_len    = udph[2];
    udph_port   = udph[1];

    wolh_off    = iph_len + 8
    wolh_len    = udph_len - 8

    if wolh_len == WOLH_PASSWD_NONE:
        wolh = struct.unpack('!102B', packet[wolh_off:wolh_off + wolh_len])
        if macaddr != None and not __wol_datacheck(macaddr, wolh):
            return False
        return True
    return False

def __handle_sigs_for(socket):
    def on_exit(signal, frame):
        socket.close()
        sys.exit()
    signal.signal(signal.SIGTERM, on_exit)
    signal.signal(signal.SIGINT, on_exit)

def main():
    port = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        sock.bind((DEFAULT_HOST, DEFAULT_PORT if port == None else port))
    except socket.error as msg:
        print ('Cannot create socket. Error: ' + str(msg[0]) + ') Message:' + str(msg[1]))
        sys.exit()

    __handle_sigs_for(sock)

    wol_found = False
    while True:
        packet = sock.recv(WOL_PACKET_MAX_BYTES)

        if __wol_pktcheck(packet) and not wol_found:
            print("Kore: <WakeUp>")
            os.system("systemctl start kodi")
            wol_found = True
        else:
            wol_found = False

if __name__ == "__main__":
    main()
