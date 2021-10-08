import socket
import json
import threading

HOST = 'localhost'
PORT = 3386

connections = dict()  # connection dictionary | username: string => ('connection': socket, 'address': string)
matches = dict()  # matches dictionary | username:string => {'other_player': string, turn: integer}


def deal_with_matches():
    while True:
        for key in matches.keys():
            if matches[key] is None:
                continue

            if matches[key]['turn'] == 1:
                source = connections[key]['connection']
                destination = connections[matches[key]['other_player']]['connection']
                data = source.recv(2048)
                print(json.loads(data)['message'])
                destination.sendall(data)  # forward move to other player
                matches[key]['turn'] = 2
            else:
                source = connections[matches[key]['other_player']]['connection']
                destination = connections[key]['connection']
                data = source.recv(2048)
                print(data.decode("utf-8"))
                destination.sendall(data)
                matches[key]['turn'] = 1


def add_to_matchmaking(username):
    for key, value in matches.items():
        if value is None:
            matches[key] = {
                'turn': 1,
                'other_player': username,
            }
            payload = {
                'is_starting': True,
                'message': 'Game ready!'
            }
            connections[key]['connection'].sendall(json.dumps(payload).encode('utf-8'))
            return 0

    matches[username] = None
    return 1


def cleanup():
    for _, value in connections.items():
        try:
            value['connection'].close()
        except:
            pass  # ignore


def main():
    global connections
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    matches_thread = threading.Thread(target=deal_with_matches)
    matches_thread.start()

    while True:
        conn, addr = server.accept()

        init_data = conn.recv(1024)
        init_data_decoded = json.loads(init_data.decode('utf-8'))
        print(init_data_decoded)
        username = init_data_decoded['name']
        if username not in connections:
            connections[username] = {
                'connection': conn,
                'address': addr
            }
            conn.sendall('Ready for matchmaking...'.encode('utf-8'))
            if add_to_matchmaking(username) == 0:
                payload = {
                    'is_starting': False,
                    'message': 'Game ready !'
                }
                conn.sendall(json.dumps(payload).encode('utf-8'))
            else:
                conn.sendall('Looking for players'.encode('utf-8'))
        else:
            conn.sendall('Username taken, try another one...'.encode('utf-8'))
            conn.close()


if __name__ == '__main__':
    main()
