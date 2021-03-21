class GateController:
    """
    Wrapper for low level communication with gate.

    ...

    TODO
    """

    def __init__(self):
        pass

    def is_busy(self):
        raise NotImplementedError

    def open(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError
