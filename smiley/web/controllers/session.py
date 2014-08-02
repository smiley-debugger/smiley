from pecan import request


class FakeSession(dict):

    def save(self):
        return


def get_session():
    return request.environ.get('beaker.session', FakeSession())
