import socket
import sys
import struct
import random
import time
import traceback
from threading import Thread

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8000
CHUNK_SIZE = 1024
PACKET_SIZE = 1030
LOSS_PROBABILITY = 0.5

packets = {}

def calculate_checksum(data):
    checksum = sum(data) % 65535
    return checksum
    
def main():
    addr = (SERVER_IP, SERVER_PORT)
    
    # Create a UDP ocket for the server
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind(addr)

    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")
    expected_seq = 0
    received = []
    with open("received.txt", "wb") as out:
        while True:
            try:
                received_packet, client_addr = soc.recvfrom(PACKET_SIZE)
                seq_num = struct.unpack("!I", received_packet[:4])[0]
                checksum = struct.unpack("!H", received_packet[4:6])[0]
                data = received_packet[6:]

                time.sleep(.1)
                if random.random() < LOSS_PROBABILITY:
                    print(f"Packet {seq_num // CHUNK_SIZE} discarded due to simulated packet loss")
                elif calculate_checksum(data) != checksum:
                    print(f"Packet {seq_num // CHUNK_SIZE} discarded due to checksum error.")
                else:
                    print("Expected:", expected_seq // CHUNK_SIZE, "Received:", seq_num // CHUNK_SIZE)
                    if(not seq_num in received):
                        out.seek(seq_num)
                        out.write(data)
                        received.append(seq_num)
                        print(f"Received and wrote packet {seq_num // CHUNK_SIZE}")
                    if(seq_num == expected_seq):
                        expected_seq += CHUNK_SIZE
                        ack_packet = struct.pack("!I", expected_seq)
                        soc.sendto(ack_packet, client_addr)
                        while(expected_seq in received):
                            expected_seq += CHUNK_SIZE
                            ack_packet = struct.pack("!I", expected_seq)
                            soc.sendto(ack_packet, client_addr)
                    else:
                        ack_packet = struct.pack("!I", expected_seq)
                        soc.sendto(ack_packet, client_addr)
            except socket.error as e:
                print(f"Socket error: {e}")
                break
        

if __name__ == "__main__":
    main()