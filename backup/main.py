from backup.server.server import ControlServer

#
# def onSigChld(signo, frame):
#     print("onSigChld")
#
#
# def onSigInt(signo, frame):
#     print("onSigInt")
#
#
# def onSigTerm(signo, frame):
#     print("onSigTerm")


if __name__ == "__main__":
    # # 子进程退出后向父进程发送的信号
    # signal.signal(signal.SIGCHLD, onSigChld)
    #
    # # 主进程退出信号
    # signal.signal(signal.SIGINT, onSigInt)
    # signal.signal(signal.SIGTERM, onSigTerm)

    controlServer = ControlServer({
        "user": "ljw",
    })
    controlServer.init_control_server()
    controlServer.run()
