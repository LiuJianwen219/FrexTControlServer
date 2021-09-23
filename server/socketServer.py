import json
import time
import random

from device.device import Device
from server.constant import *

# MAX_LENGTH = 200
# deviceAll = 6

devices = {}
user = {}

UTDmap = {}
DTUmap = {}

# rabbitMQClient = None

tempCount = 0


# Called for every client connecting (after handshake)
def new_client(client, server):
    print("New client connected and was given id %d" % client['id'])
    # server.send_message_to_all(json.dumps({"type": 1000, "info": "new client in"}).encode("utf-8"))
    data = {'type': WHO_YOU_ARE}
    server.send_message(client, json.dumps(data))
    print("WHO_YOU_ARE")


# Called for every client disconnecting
def client_left(client, server):
    if client['id'] in user:
        print("user(%d) disconnected" % client['id'])
        if UTDmap[client['id']]:  # 用户非正常退出
            data = {'type': ACT_RELEASE,
                    'content': {'device': devices[UTDmap[client['id']]].getId(), 'time': time.time()}}
            server.send_message(devices[UTDmap[client['id']]].getClient(), json.dumps(data))
            devices[UTDmap[client['id']]].writeState(0, time.time())
            DTUmap[UTDmap[client['id']]] = None
            UTDmap[client['id']] = None
        user.pop(client['id'])
        return

    if client['id'] in devices:  # 设备非正常退出
        if DTUmap[client['id']]:
            print("device(%d) disconnected" % client['id'])
            data = {'type': ACT_RELEASE, 'content': {'device': devices[client['id']].getId(), 'time': time.time()}}
            server.send_message(user[DTUmap[client['id']]], json.dumps(data))
            devices[client['id']].writeState(-1, time.time())
            UTDmap[DTUmap[client['id']]] = None
            DTUmap[client['id']] = None
        devices.pop(client['id'])
        return

    print("other client(%d) disconnected" % client['id'])


# Called when a client sends a message
def message_received(client, server, message):
    # print("Client(%d) said: %s" % (client['id'], json.loads(message)))
    # print("Client(%d) said: %s" % (client['id'], json.loads(message)['type']))

    def sendUTD(data):
        server.send_message(devices[UTDmap[client['id']]].getClient(), json.dumps(data))

    def sendDTU(data):
        server.send_message(user[DTUmap[client['id']]], json.dumps(data))

    dict_ = json.loads(message)

    if dict_['type'] == AUTH_DEVICE:
        devices[client['id']] = Device(dict_['index'])
        DTUmap[client['id']] = None
        data = {'type': AUTH_SUCC_DEVICE, 'content': {'info': "OK"}}
        server.send_message(client, json.dumps(data))

    elif dict_['type'] == AUTH_USER:
        user[client['id']] = client
        UTDmap[client['id']] = None
        data = {'type': AUTH_SUCC_USER, 'content': {'info': "OK"}}
        server.send_message(client, json.dumps(data))

    elif dict_['type'] == AUTH_RABBIT:
        # global rabbitMQClient
        # if rabbitMQClient == None:
        #    rabbitMQClient = client['id']

        user[client['id']] = client
        UTDmap[client['id']] = None

        data = {'type': AUTH_RABBIT_SUCC, 'content': {'info': "OK"}}
        server.send_message(client, json.dumps(data))
        # else:
        #    data = {'type': AUTH_RABBIT_FAIL, 'content': {'info': "重复"}}
        #    server.send_message(client, json.dumps(data))

    elif dict_['type'] == UPDATE_DEVICE:  # 控制器们向服务器发送的数据更新信息，并保证只有这个进程在写
        if dict_['time'] > devices[client['id']].getTime():
            devices[client['id']].writeState(dict_['state'], dict_['time'])
            devices[client['id']].setClient(client, dict_['time'])

        global tempCount
        if tempCount % 5 == 0:
            for key in devices:
                print(devices[key].readState())
        tempCount += 1
        # print('beat...')
        data = {'type': UPDATE_DEVICE_SUCC, 'content': {'info': "OK"}}
        server.send_message(client, json.dumps(data))

    elif dict_['type'] == ACT_SYNC:
        if client['id'] in user:
            nReady, nBusy, nError = countDevice()

            data = {'type': SYNC_DEVICE, 'content': {'nReady': nReady, 'nBusy': nBusy, 'nError': nError}}
            server.send_message(client, json.dumps(data))
        else:
            data = {'type': AUTH_FAIL_USER, 'content': {'info': "登录超时，请重新登录"}}
            server.send_message(client, json.dumps(data))
    elif dict_['type'] == ACT_ACQUIRE:
        if client['id'] in user:
            if UTDmap[client['id']]:
                data = {'type': ACQUIRE_SUCC, 'content': {'info': "重新获取设别前，请先释放"}}
                sendUTD(data)
                return

            nReady, nBusy, nError = countDevice()

            if nReady > 0:
                acquire = randomGetOne()

                devices[acquire].writeState(1, time.time())

                UTDmap[client['id']] = acquire

                if dict_['using'] == 'exp':
                    data = {'type': ACQUIRE_DEVICE_FOR_EXP, 'content': {'Uid': client['id']}}
                    sendUTD(data)
                    return
                elif dict_['using'] == 'test':
                    data = {'type': ACQUIRE_DEVICE_FOR_TEST, 'content': {'Uid': client['id']}}
                    sendUTD(data)
                    return

            else:
                data = {'type': ACQUIRE_FAIL, 'content': {'info': "all devices busy"}}
                server.send_message(client, json.dumps(data))
        else:
            data = {'type': AUTH_USER_FILE, 'content': {'info': "登录超时，请重新登录"}}
            server.send_message(client, json.dumps(data))

    elif dict_['type'] == ACT_SYNC_SW_BTN:
        data = {'type': ACT_SYNC_SW_BTN}
        sendUTD(data)
    elif dict_['type'] == ACT_SYNC_SW_BTN_SUCC:
        sendDTU(dict_)

    elif dict_['type'] == ACQUIRE_DEVICE_SUCC_EXP:
        DTUmap[client['id']] = dict_['content']['Uid']
        data = {'type': ACQUIRE_SUCC, 'content': {'device': dict_['content']['device'], 'info': "OK"}}
        sendDTU(data)
    elif dict_['type'] == ACQUIRE_DEVICE_SUCC_TEST:
        DTUmap[client['id']] = dict_['content']['Uid']
        data = {'type': ACQUIRE_SUCC, 'content': {'device': dict_['content']['device'], 'info': "OK"}}
        sendDTU(data)
    elif dict_['type'] == ACT_RELEASE:
        if UTDmap[client['id']]:
            data = {'type': ACT_RELEASE, 'content': {'device': dict_['content']['device'], 'time': time.time()}}
            sendUTD(data)

            devices[UTDmap[client['id']]].writeState(0, time.time())
            DTUmap[UTDmap[client['id']]] = None
            UTDmap[client['id']] = None

    elif dict_['type'] == OP_SW_OPEN:
        print("OP_SW_OPEN")
        data = {'type': OP_SW_OPEN_DEVICE, 'content': {'id': dict_['content']['id'], 'changeTo': 1}}
        sendUTD(data)
    elif dict_['type'] == OP_SW_CLOSE:
        print("OP_SW_CLOSE")
        data = {'type': OP_SW_CLOSE_DEVICE, 'content': {'id': dict_['content']['id'], 'changeTo': 0}}
        sendUTD(data)
    elif dict_['type'] == OP_SW_CHANGED:
        print("OP_SW_CHANGED")
        sendDTU(dict_)

    elif dict_['type'] == OP_BTN_PRESS:
        print("OP_BTN_PRESS")
        data = {'type': OP_BTN_PRESS_DEVICE, 'content': {'id': dict_['content']['id'], 'changeTo': 1}}
        sendUTD(data)
    elif dict_['type'] == OP_BTN_RELEASE:
        print("OP_BTN_RELEASE")
        data = {'type': OP_BTN_RELEASE_DEVICE, 'content': {'id': dict_['content']['id'], 'changeTo': 0}}
        sendUTD(data)
    elif dict_['type'] == OP_BTN_CHANGED:
        sendDTU(dict_)

    elif dict_['type'] == OP_PS2_SEND:
        sendUTD(dict_)

    elif dict_['type'] == OP_PS2_SEND_SUCC:
        sendDTU(dict_)

    elif dict_['type'] == OP_PROGRAM:
        sendUTD(dict_)
    elif dict_['type'] == OP_PROGRAM_SUCC:
        sendDTU(dict_)
    elif dict_['type'] == TEST_PROGRAM:
        sendUTD(dict_)
    elif dict_['type'] == TEST_PROGRAM_SUCC:
        sendDTU(dict_)
    elif dict_['type'] == TEST_PROGRAM_FAIL:
        sendDTU(dict_)

    elif dict_['type'] == REQ_SEG:  # 废弃
        sendUTD(dict_)
    elif dict_['type'] == REQ_SEG_SUCC:  # 废弃
        sendDTU(dict_)
    elif dict_['type'] == REQ_LED:  # 废弃
        sendUTD(dict_)
    elif dict_['type'] == REQ_LED_SUCC:  # 废弃
        sendDTU(dict_)

    elif dict_['type'] == REQ_READ_DATA:
        sendUTD(dict_)
    elif dict_['type'] == REQ_READ_DATA_SUCC:
        sendDTU(dict_)

    elif dict_['type'] == TEST_READ_RESULT:
        sendUTD(dict_)
    elif dict_['type'] == TEST_READ_RESULT_SUCC:
        sendDTU(dict_)

    elif dict_['type'] == INIT_FILE_UPLOAD:
        sendUTD(dict_)
    elif dict_['type'] == INIT_FILE_UPLOAD_SUCC:
        sendDTU(dict_)

    else:
        pass
        # if dict_['type'] == UTD_SW_DOWN:
        #     server.send_message(UTD_sock[client['id']]['sock'], message)
        # elif dict_['type'] == UTD_SW_UP:
        #     server.send_message(UTD_sock[client['id']]['sock'], message)
        # elif dict_['type'] == DTU_SW_DOWN:
        #     server.send_message(DTU_sock[client['id']]['sock'], message)
        # elif dict_['type'] == DTU_SW_UP:
        #     server.send_message(DTU_sock[client['id']]['sock'], message)


def randomGetOne():
    tmp = devices
    for i in range(0, len(devices)):
        a = random.sample(tmp.keys(), 1)  # 随机一个字典中的key，第二个参数为限制个数
        b = a[0]
        if tmp[b].readState() == 0:
            return b
        del tmp[b]  # 删除已抽取的键值对
    return -1


def countDevice():
    nReady = 0
    nBusy = 0
    nError = 0
    for item in devices:
        if devices[item].readState() == 0:
            nReady += 1
        elif devices[item].readState() == 1:
            nBusy += 1
        else:
            nError += 1
    return nReady, nBusy, nError

# # 读取devices的状态
# def upDateDevice():
#     devices_state.clear()
#     for i in range(deviceAll):
#         device = {
#             "id": "device%02d" % i,
#             "state": -1
#         }
#         devices_state.append(device)
#
#     curtime = time.time()
#     with open("./device.info", "r+") as f:
#         mm = mmap.mmap(fileno=f.fileno(), length=0)
#         for i in range(deviceAll):
#             mm.seek(i * MAX_LENGTH)
#             l = mm.read_byte()
#             info = mm.read(l)
#             # print(type(info))
#             info = json.loads(info.decode("utf-8"))
#             # print(info)
#             # print(info["time"] + 10)
#             if info["time"] + SYS_DELAY > curtime:  #共享内存中的时间戳如果距离现在SYS_DELAY秒以内则更新，否则认为故障
#                 # print(devices_state[i]["state"])
#                 # print(info["device"]["state"])
#                 devices_state[i]["state"] = info["device"]["state"]
#             else:
#                 devices_state[i]["state"] = -1
#
#     # for i in range(deviceAll):
#     #     print(devices[i])
#     #
#     # data = {
#     #     'type': UPDATE_DEVICE,
#     #     "time": curtime,
#     #     "devices": devices
#     # }
#     # ws.send(json.dumps(data))
#     Timer(UPDATE_TIME, upDateDevice).start()
