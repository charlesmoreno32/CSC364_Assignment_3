import socket
import struct
import time
import csv

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8000
CHUNK_SIZE = 1024
PACKET_SIZE = 1030

def calculate_checksum(data):
    checksum = sum(data) % 65535
    return checksum

def main():
    addr = (SERVER_IP, SERVER_PORT)
    
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.settimeout(.5)

    with open("gistfile1.txt", "rb") as file:
        file_data = file.read()

    chunks = []
    for i in range(0, len(file_data), CHUNK_SIZE):
        chunks.append(file_data[i:i + CHUNK_SIZE])
    
    cwnd = 1
    ssthresh = 100
    window_start = 0
    seq_num = 0
    window = {}
    RTTs = {}
    dup_ack = 0
    last_ack = -1
    repeated = []
    retransmissions = 0

    # While there is still unacknowledged packets
    with open("cwnd_vs_rtt.csv", "w", newline='') as cwnd_file, open("retransmissions_vs_time.csv", "w", newline='') as retrans_file:
        
        cwnd_writer = csv.writer(cwnd_file)
        retrans_writer = csv.writer(retrans_file)
        cwnd_writer.writerow(["RTT", "cwnd"])
        retrans_writer.writerow(["Time", "Retransmissions"])
        rtt_counter = 0
        start_time = time.time()

        while window_start < len(chunks) * CHUNK_SIZE:
            # Send the packets over within the window
            while window_start <= seq_num and seq_num < window_start + cwnd * CHUNK_SIZE and seq_num < len(chunks) * CHUNK_SIZE:
                chunk_index = seq_num // CHUNK_SIZE
                chunk = chunks[chunk_index]
                checksum = calculate_checksum(chunk)
                # Send packet to server
                packet = struct.pack("!I", seq_num) + struct.pack("!H", checksum) + chunk
                soc.sendto(packet, addr)
                # Put packet in window (it's now unack) and track time
                window[seq_num] = packet
                #print("Sent", seq_num // CHUNK_SIZE)
                RTTs[seq_num] = time.time()
                seq_num += CHUNK_SIZE
            try:
                received_packet, _ = soc.recvfrom(4)
                #print("----")
                if not received_packet:
                    print("Disconnected from server")
                    return
                ack_num = struct.unpack("!I", received_packet[:4])[0]

                #Log first time RTT complete for specfic packet
                if ack_num - CHUNK_SIZE in RTTs and not (ack_num - CHUNK_SIZE) in repeated:
                    if(cwnd >= ssthresh):
                        cwnd += 1
                    repeated.append(ack_num - CHUNK_SIZE)
                    rtt = time.time() - RTTs[ack_num - CHUNK_SIZE]
                    RTTs[ack_num - CHUNK_SIZE] = rtt
                    rtt_counter += 1
                    cwnd_writer.writerow([rtt_counter, cwnd])
                    retrans_writer.writerow([rtt_counter, retransmissions])
                    print(f"RTT for packet {(ack_num - CHUNK_SIZE) // CHUNK_SIZE}: {rtt:.4f} seconds")
                
                # Check for duplicate ACKs
                if ack_num == last_ack:
                    dup_ack += 1
                    if dup_ack >= 3:
                        print(f"Duplicate ACK retransmit for packet {ack_num // CHUNK_SIZE}")
                        #print("Window start:", window_start // CHUNK_SIZE, "ACK:", ack_num // CHUNK_SIZE)
                        if ack_num in window:
                            soc.sendto(window[ack_num], addr)
                        else:
                            print(f"Packet with seq_num {ack_num // CHUNK_SIZE} not in window.")
                        cwnd = 1
                        dup_ack = 0
                        retransmissions += 1
                        #retrans_writer.writerow([time.time() - start_time, retransmissions])
                        continue
                else:
                    dup_ack = 0
                    last_ack = ack_num

                if(cwnd < ssthresh):
                    cwnd += 1

                #Update and slide window
                #print("Window start:", window_start // CHUNK_SIZE, "Ack packet:", (ack_num) // CHUNK_SIZE)
                if (ack_num - CHUNK_SIZE == window_start) and window_start in window:
                    print("Window done with:", window_start // CHUNK_SIZE)
                    del window[window_start]
                    window_start = ack_num

            except socket.timeout:
                print(f"Timeout, retransmitting packet {window_start // CHUNK_SIZE}")
                cwnd = 1
                retransmissions += 1
                #retrans_writer.writerow([time.time() - start_time, retransmissions])
                soc.sendto(window[window_start], addr)
        

            
if __name__ == "__main__":
    main()