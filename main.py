import socket
import json
import game_logic


def get_address():
    with open('config.bin', 'rb') as f:
        data = f.read()
    return ''


HOST = get_address()
PORT = 3386


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((HOST, PORT))
    matched = False

    name = input("Input your username: ")
    payload = {
        'name': name,
    }
    server.sendall(json.dumps(payload).encode('utf-8'))
    is_starting = False

    while not matched:
        response = server.recv(1024)
        print(response.decode('utf-8'))
        try:
            data = json.loads(response.decode('utf-8'))
        except json.JSONDecodeError:
            continue
        else:
            is_starting = data['is_starting']
            matched = True

    if matched:
        game_logic.game_loop(server, is_starting)


if __name__ == '__main__':
    main()
