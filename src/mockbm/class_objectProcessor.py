"""Mock function/class used in objectProcessor"""


def mockFunctionToPass():
    pass


def sqlQueryMock(*args):
    return [(None, "mockData"),]


def sqlExecuteMock(*args):
    return


class SqlReadyMock(object):
    """Mock helper_sql.sql_ready event with dummy class"""
    @staticmethod
    def wait(time):
        """Don't wait, return immediately"""
        return
