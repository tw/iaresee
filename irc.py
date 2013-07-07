__author__ = 'tobiewarburton'
import socket
import re

class RawMessage:
    def __init__(self, command, prefix, params, trail):
        self.command = command
        self.prefix = prefix
        self.params = params
        self.trail = trail

    def handle(self, bot):
        if self.command == 'PING':
            bot.send_raw('PONG ' + self.trail)
        print self

    def __str__(self):
        return 'RAW %s %s %s %s' % (self.command, self.prefix, self.params,
                                    self.trail)
 
    @staticmethod
    def parse(data):
        if data['command'].isdigit():
            return NumericMessage(int(data['command']), data['prefix'],
                                  data['params'], data['trail'])
        elif data['command'] == 'PRIVMSG':
            return PrivMessage(data['prefix'], data['params'], data['trail'])
        else:
            return RawMessage(data['command'], data['prefix'], data['params'],
                              data['trail'])


class NumericMessage:
    def __init__(self, numeric, prefix, params, trail):
        self.numeric = numeric
        self.prefix = prefix
        self.params = params
        self.trail = trail

    def handle(self, bot):
        pass

    def __str__(self):
        return 'NUMERIC (%d) %s %s %s' % (self.numeric, self.prefix,
                                          self.params, self.trail)


class PrivMessage:
    def __init__(self, sender, destination, msg):
        self.nick, self.user, self.host = re.search(r'(.*)!(.*)@(.*)',
                                                    sender).groups()
        self.destination = destination
        self.msg = msg

    def is_channel(self):
        return self.destination.startswith('#')

    def is_private(self):
        return not is_channel()

    def __str__(self):
        if self.is_channel():
            return '[ %s ] <%s> %s' % (self.destination, self.nick, self.msg)
        else:
            return '<%s> %s' % (self.nick, self.msg)


class Bot:

    def __init__(self, server, port, nick, channels):
        self.server = server
        self.port = port
        self.channels = channels
        self.nick = nick
        self.socket = socket.socket()

    def send_raw(self, raw):
        self.socket.send('%s\r\n' % raw)

    def connect(self):
        self.socket.connect((self.server, self.port))
        self.file = self.socket.makefile('r')
        self.send_raw('NICK %s' % self.nick)
        self.send_raw('USER %s %s %s :warb0' %
                       (self.nick, self.nick, self.nick))
        for channel in self.channels:
            self.send_raw('JOIN %s' % channel)

    def listen(self):
        while True:
            line = self.file.readline().replace('\r', '').strip()
            if not line:
                break
            # we have a line!
            self.handle(line)

    def handle(self, line):
        irc_regex = re.compile(
                r'^(:(?P<prefix>\S+) )?(?P<command>\S+)( (?!:)(?P<params>.+?))?( :(?P<trail>.+))?$'
                )
        matched = irc_regex.match(line)
        data = matched.groupdict()
        msg = RawMessage.parse(data)
        if isinstance(msg, PrivMessage):
            print msg
        elif isinstance(msg, NumericMessage):
            msg.handle(self)
        else:
            msg.handle(self)


if __name__ == '__main__':
    bot = Bot('irc.rizon.net', 6667, 'warb0t', ['#aurora-rs'])
    bot.connect()
    bot.listen()
