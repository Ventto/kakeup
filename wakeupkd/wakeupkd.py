#!/usr/bin/env python
import os
import signal
import socket
import sys
import struct

WOLH_PASSWD_NONE     = 102
WOLH_PASSWD_EXIST    = 106
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

def __wol_pwdcheck(passwd, data):
    if passwd.nbytes() != 4:
        return False
    pwd_bytes = bytearray(passwd)
    for i in range(4):
        if pwd_bytes[i] != data[i]:
            return False
    return False

def __wol_pktcheck(packet, macaddr = None, ipsrc = None, passwd = None):
    size = __get_size(packet)
    if size < WOL_PACKET_MIN_BYTES:
        return False

    iph         = struct.unpack('!BBHHHBBH4s4s' , packet[0:20])
    iph_version = iph[0] >> 4
    iph_len     = (iph[0] & 0xF) * 4
    iph_ipsrc   = iph[8]
    iph_ipdst   = iph[9]

    if ipsrc != None and ipsrc != iph_src:
        return False

    udph        = struct.unpack('!4H' , packet[iph_len: iph_len + 8])
    udph_len    = udph[2];
    udph_port   = udph[1];

    wolh_off    = iph_len + 8
    wolh_len    = udph_len - 8

    if wolh_len == WOLH_PASSWD_NONE or wolh_len == WOLH_PASSWD_EXIST:
        wolh = struct.unpack('!102B', packet[wolh_off:wolh_off + wolh_len])
        if macaddr != None and not __wol_datacheck(macaddr, wolh):
            return False
        if passwd != None and wolh_len == WOL_PASSWD_EXIST:
            pwd_off = wolh_off + wolh_len
            return __wol_pwdcheck(passwd, packet[pwd_off: pwd_off + 4])
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

    while True:
        packet = sock.recv(WOL_PACKET_MAX_BYTES)
        if __wol_pktcheck(packet):
            print("WOL !")
            os.system("systemctl start kodi")

if __name__ == "__main__":
    main()