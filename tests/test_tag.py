import unittest

from usage import tag


class TestSuperTag(unittest.TestCase):
    """Tests the SuperTag class"""
    def test_init(self):
        supertag = tag.SuperTag()
        self.assertTrue(isinstance(supertag['tag_set'], set))
        self.assertTrue(isinstance(supertag['tags'], dict))

    def test_track(self):
        supertag = tag.SuperTag()
        supertag.track('testtag', 'a')
        supertag.track('TestTag', 'b')

        self.assertEquals(set(['testtag', 'TestTag']), supertag['tag_set'])
        self.assertEquals(set(['a']), supertag['tags']['testtag'])
        self.assertEquals(set(['b']), supertag['tags']['TestTag'])


class TestTracker(unittest.TestCase):
    """Tests the tracker class."""
    tracker = tag.Tracker()

    tracker.track('appid', 'someapp')
    tracker.track('appID', 'otherapp')
    tracker.track('color', 'RED')
    tracker.track('colOR', 'green')
    tracker.track('env', 'dev')
    tracker.track('env', 'prod')

    import pprint
    pprint.pprint(tracker)
