import api


if __name__ == '__main__':
    prosper = api.Prosper(sandbox=False)
    prosper.account()
    prosper.notes()
