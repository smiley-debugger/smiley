import pstats
import profile
import unittest

from smiley import stats


class StatsEncodeTest(unittest.TestCase):

    def setUp(self):
        super(StatsEncodeTest, self).setUp()
        self.stats = pstats.Stats(profile.Profile())

    def test_to_blob(self):
        stats.stats_to_blob(self.stats)

    def test_from_blob(self):
        b = stats.stats_to_blob(self.stats)
        s = stats.blob_to_stats(b)
        assert isinstance(s, pstats.Stats)
