class ScriptExit(Exception):
    pass


def runseg(reporter, scr, state):
    state['global']['report'] = reporter
    try:
        exec(scr, state['global'], state['local'])
        del state['global']['report']
        return True
    except SystemExit:
        print("Script exit early")
        return False
    except Exception as e:
        print("Encountered error when running:")
        print(e)
        print("Script:\n{}".format(scr))
        return False
