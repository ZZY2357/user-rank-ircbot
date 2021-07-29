import socket
import ssl

rank = {}

def get_sorted_rank():
    usernames = list(rank.keys())
    output = ''
    for i in range(len(usernames) - 1):
        for j in range(len(usernames) - i - 1):
            if rank[usernames[j]] < rank[usernames[j + 1]]:
                rank[usernames[j]], rank[usernames[j + 1]] = \
                    rank[usernames[j + 1]], rank[usernames[j]]
    for i in usernames:
        output += f'{ i }: { rank[i] }\n'
    return (output)

def save_data():
    with open('data.txt', 'w') as f:
        f.write(get_sorted_rank())

def load_data():
    global rank

    with open('data.txt', 'r') as f:
        content = f.read().strip()
        if content.strip() == '':
            return
    for i in content.split('\n'):
        rank[i.split(': ')[0]] = int(i.split(': ')[1])


class IRCBot:
    def __init__(self, address, name, channel):
        self.address = address
        self.socket = ssl.wrap_socket(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        )
        self.name = name
        self.channel = channel

    def send(self, msg):
        self.socket.send(f'{ msg }\r\n'.encode())
    
    def send_message(self, msg):
        self.send(f'PRIVMSG { self.channel } :{ msg }')

    def connect(self):
        self.socket.connect(self.address)
        self.send(f'NICK { self.name }')
        self.send('USER {0} {0} {0} :{0}'.format(self.name))

        self.send(f'JOIN { self.channel }')

    def process(self):
        global rank

        message = self.socket.recv(1024).decode()

        print(message)

        for i in message.split('\n'):
            if i.startswith('PING'):
                self.send(i.replace('PING', 'PONG', 1))

            if 'PRIVMSG' in i and '!~' in i:
                if '!exit' in i or '!quit' in i or '!shutdown' in i:
                    save_data()
                    exit()
                username = i.split('!')[0][1:]
                if username in rank.keys():
                    rank[username] += 1
                else:
                    rank[username] = 1
                print('rank: ' + get_sorted_rank())

                if '!rank' in i:
                    self.send_message(get_sorted_rank())

load_data()

address = ('irc.libera.chat', 6697)
bot = IRCBot(address, 'HotBot', '#linuxba')
bot.connect()

while True:
    bot.process()
