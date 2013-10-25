import unittest
from pyspotprice import (parse_prices, GOLD_KEY,
        SILVER_KEY, PLATINUM_KEY)
PLATINUM_KEY

class ParsePricesTest(unittest.TestCase):
    def setUp(self):
        super(ParsePricesTest, self).setUp()
        self.content = open('test_response.html').read()

    def test_gets_prices(self):
        prices_dict = parse_prices(self.content)

        gold_info = prices_dict[GOLD_KEY]
        #print '\n'.join("{}={}".format(i, str(c)) for i, c in
        #        enumerate(gold_info.info_cells))

        self.assertEqual(gold_info.date, '10/24/2013')
        self.assertEqual(gold_info.time_est, '17:14')
        self.assertEqual(gold_info.bid_cents, 134730)
        self.assertEqual(gold_info.ask_cents, 134830)
        self.assertEqual(gold_info.change_usd_cents, 1360)
        self.assertEqual(gold_info.change_percent, 1.02)

        silver_info = prices_dict[SILVER_KEY]
        self.assertEqual(silver_info.date, '10/24/2013')
        self.assertEqual(silver_info.time_est, '17:15')
        self.assertEqual(silver_info.bid_cents, 2272)
        self.assertEqual(silver_info.ask_cents, 2282)
        self.assertEqual(silver_info.change_usd_cents, 16)
        self.assertEqual(silver_info.change_percent, .71)


        platinum_info = prices_dict[PLATINUM_KEY]
        self.assertEqual(platinum_info.date, '10/24/2013')
        self.assertEqual(platinum_info.time_est, '17:03')
        self.assertEqual(platinum_info.bid_cents, 144600)
        self.assertEqual(platinum_info.ask_cents, 145600)
        self.assertEqual(platinum_info.change_usd_cents, 1800)
        self.assertEqual(platinum_info.change_percent, 1.26)



if __name__ == '__main__':
    unittest.main()
