import datetime

from server.constant import *


def time_now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')


def time_before(seconds):
    return (datetime.datetime.now() - datetime.timedelta(seconds=seconds)).strftime('%Y-%m-%d %H:%M:%S.%f')


class Device:

    def __init__(self, id, tags):
        self.id = id
        self.syncTime = time_now()
        self.state = -1
        self.client = None
        if not tags:
            self.tags = ["TESTING"]
        else:
            self.tags = tags
        # self.user = None

    def getId(self):
        return self.id

    def readState(self):
        curTime = time_before(150)
        if self.syncTime > curTime:
            return self.state
        # print(self.syncTime)
        # print(curTime)
        return -1

    def writeState(self, s, t):
        # print(self.syncTime)
        # print(t)
        if self.syncTime <= t:
            self.syncTime = t
            self.state = s
            # print("修改" + str(s))

    def setClient(self, c, t):
        if self.syncTime <= t:
            self.syncTime = t
            self.client = c

    # def setUser(self, u, t):
    #     if self.syncTime < t:
    #         self.syncTime = t
    #         self.user = u

    def getClient(self):
        curTime = time_now()
        if self.syncTime <= curTime:
            return self.client

    # def getUser(self):
    #     curTime = time_now()
    #     if self.syncTime < curTime:
    #         return self.user

    def getTime(self):
        return self.syncTime

    def toDict(self):
        return {
            'id': self.id,
            'syncTime': self.syncTime.__str__(),
            'state': self.state,
            'clientId': self.client['id'],
            'tag': self.tags,
            # 'user': self.user
        }

    def isMatchTags(self, tag):
        return tag in self.tags
