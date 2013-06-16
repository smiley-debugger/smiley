import testtools

from smiley import uuidstack


class UUIDStackTest(testtools.TestCase):

    def setUp(self):
        self.stack = uuidstack.UUIDStack()
        super(UUIDStackTest, self).setUp()

    def test_empty(self):
        self.assertEqual(self.stack._stack, [])
        self.assertEqual(self.stack.top(), None)

    def test_push(self):
        self.stack.push()
        self.assertEqual(len(self.stack._stack), 1)

    def test_top(self):
        self.stack.push()
        t = self.stack.top()
        self.assertTrue(t)

    def test_pop(self):
        self.stack.push()
        t1 = self.stack.top()
        t2 = self.stack.pop()
        self.assertEqual(t1, t2)
        self.assertEqual(self.stack._stack, [])
