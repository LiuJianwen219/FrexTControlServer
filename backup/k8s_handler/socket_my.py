import sys, getopt


def main(argv):
    global opts
    values = {}
    try:
        opts, args = getopt.getopt(argv, "u:d:", [
            "user=", "device=",
        ])
    except getopt.GetoptError:
        print('we need help 2.')
        print(opts)
    finally:
        print(opts)

    for opt, arg in opts:
        if opt == '-h':
            print('we need help 3.')
            print(opts)
        elif opt in ("-u", "--user"):
            values["user"] = arg
        elif opt in ("-d", "--device"):
            values["device"] = arg

    print(values["user"])
    print(values["device"])



