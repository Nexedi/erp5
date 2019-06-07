from ZServer.datatypes import ServerFactory

class TimerServerFactory(ServerFactory):
    def __init__(self, section):
        ServerFactory.__init__(self)
        self.interval = section.interval

    def create(self):
        from timerserver.TimerServer import TimerServer
        return TimerServer(self.module, self.interval)
