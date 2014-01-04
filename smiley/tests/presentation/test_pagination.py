import testscenarios

from smiley.presentation import pagination


class PaginationTest(testscenarios.TestWithScenarios):

    scenarios = [

        ('1 of 20', {'page': 1,
                     'per_page': 5,
                     'num_items': 5 * 20,
                     'expected': [(1, 5), (20, 20)]}),
        ('2 of 20', {'page': 2,
                     'per_page': 5,
                     'num_items': 5 * 20,
                     'expected': [(1, 5), (20, 20)]}),
        ('10 of 20', {'page': 10,
                      'per_page': 5,
                      'num_items': 5 * 20,
                      'expected': [(1, 1), (8, 12), (20, 20)]}),
        ('19 of 20', {'page': 19,
                      'per_page': 5,
                      'num_items': 5 * 20,
                      'expected': [(1, 1), (16, 20)]}),
        ('20 of 20', {'page': 20,
                      'per_page': 5,
                      'num_items': 5 * 20,
                      'expected': [(1, 1), (16, 20)]}),

        ('1 of 5', {'page': 1,
                    'per_page': 5,
                    'num_items': 5 * 5,
                    'expected': [(1, 5)]}),
        ('2 of 5', {'page': 2,
                    'per_page': 5,
                    'num_items': 5 * 5,
                    'expected': [(1, 5)]}),

        ('1 of 7', {'page': 1,
                    'per_page': 5,
                    'num_items': 5 * 7,
                    'expected': [(1, 7)]}),

    ]

    def test(self):
        actual = pagination.get_pagination_values(self.page,
                                                  self.per_page,
                                                  self.num_items)
        self.assertEqual(self.expected, actual['page_ranges'])
