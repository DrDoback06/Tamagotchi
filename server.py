# server.py
import socket
import threading
import json

HOST = 'localhost'
PORT = 9999
clients = []
waiting_player = None

def handle_client(conn, addr):
    global waiting_player
    print(f"[Server] Client {addr} connected")
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            message = data.decode()
            msg_obj = json.loads(message)

            if msg_obj["type"] == "JOIN_LOBBY":
                if waiting_player is None:
                    # The first client to JOIN_LOBBY
                    waiting_player = {
                        "conn": conn,
                        "addr": addr,
                        "creature": msg_obj["creature"]
                    }
                    print(f"[Server] {addr} is now waiting as player1.")
                else:
                    # The second client to JOIN_LOBBY is player2
                    other_conn = waiting_player["conn"]
                    other_creature = waiting_player["creature"]
                    other_addr = waiting_player["addr"]

                    # Construct the messages
                    start_msg_waiting = {
                        "type": "BATTLE_START",
                        "player_creature": other_creature,
                        "opponent_creature": msg_obj["creature"],
                        "your_role": "player1",
                        "current_turn": "player1"
                    }
                    start_msg_new = {
                        "type": "BATTLE_START",
                        "player_creature": msg_obj["creature"],
                        "opponent_creature": other_creature,
                        "your_role": "player2",
                        "current_turn": "player1"
                    }

                    # Debug prints
                    print(f"[Server] Matching {addr} (player2) with {other_addr} (player1).")
                    print("[Server] SENDING TO PLAYER1:")
                    print(json.dumps(start_msg_waiting, indent=4))
                    print("[Server] SENDING TO PLAYER2:")
                    print(json.dumps(start_msg_new, indent=4))

                    # Send the messages
                    try:
                        other_conn.sendall(json.dumps(start_msg_waiting).encode())
                    except Exception as e:
                        print(f"[Server] Error sending to {other_addr}: {e}")
                    try:
                        conn.sendall(json.dumps(start_msg_new).encode())
                    except Exception as e:
                        print(f"[Server] Error sending to {addr}: {e}")

                    waiting_player = None
            else:
                broadcast_to_others(conn, message)
        except Exception as e:
            print(f"[Server] Error with {addr}: {e}")
            break

    print(f"[Server] Client {addr} disconnected")
    if waiting_player and waiting_player["conn"] == conn:
        waiting_player = None
    try:
        conn.close()
    except Exception:
        pass

def broadcast_to_others(sender_conn, message):
    for c in clients[:]:
        if c != sender_conn:
            try:
                c.sendall(message.encode())
            except Exception as e:
                print("[Server] Error broadcasting:", e)
                try:
                    clients.remove(c)
                except Exception:
                    pass

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[Server] Listening on {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        clients.append(conn)
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
