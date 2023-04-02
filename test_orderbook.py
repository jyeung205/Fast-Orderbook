import unittest
from orderbook import OrderBook


class TestOrderBook(unittest.TestCase):
    def test_place_first_limit_order(self):
        """
        Add order to new price in orderbook
        - check if order exists in order_id map
        - check if order exists in OrderList in corresponding price value
        - check if best bid/ask has been updated
        - check if volume at price is correct
        """

        order_book = OrderBook()
        order = {
            'type': 'limit',
            "price": 100,
            'qty': 10,
            'side': 'bid',
            'order_id': 1
        }
        order_book.parse_input(order)
        self.assertIn(order['order_id'], order_book.order_id_map)
        self.assertEqual(order_book.order_id_map[order['order_id']], order_book.bids[order['price']].head)
        self.assertEqual(order['price'], order_book.get_best_bid())
        self.assertEqual(order['qty'], order_book.get_bid_volume_at_limit_price(order['price']))

    def test_place_limit_order_at_existing_price(self):
        """
        Add order to existing price in orderbook
        - check if order exists in order_id map
        - check if order exists at tail in OrderList at corresponding price value
        - check if volume at price is correct
        """
        order_book = OrderBook()
        orders = [
            {
                'type': 'limit',
                "price": 100,
                'qty': 10,
                'side': 'bid',
                'order_id': 1
            },
            {
                'type': 'limit',
                "price": 100,
                'qty': 19,
                'side': 'bid',
                'order_id': 2
            }
        ]
        for order in orders:
            order_book.parse_input(order)
        order_id = 2
        order_price = 100
        volume = 10 + 19
        self.assertEqual(order_book.order_id_map[order_id], order_book.bids[order_price].tail, order_book.bids[order_price].head.next)
        self.assertEqual(volume, order_book.get_bid_volume_at_limit_price(order_price))

    def test_place_order_at_new_price(self):
        """
        Add order to new price in orderbook
        - check if order exists in order_id map
        - check if order exists in OrderList in corresponding price value
        - check if best bid/ask has been updated
        """
        order_book = OrderBook()
        orders = [
            {
                'type': 'limit',
                "price": 100,
                'qty': 10,
                'side': 'bid',
                'order_id': 1
            },
            {
                'type': 'limit',
                "price": 101,
                'qty': 19,
                'side': 'bid',
                'order_id': 2
            }
        ]
        for order in orders:
            order_book.parse_input(order)
        order_id = 2
        order_price = 101
        volume = 19
        self.assertIn(order_id, order_book.order_id_map)
        self.assertEqual(order_book.order_id_map[order_id], order_book.bids[order_price].head)
        self.assertIn(100, order_book.bids)
        self.assertIn(101, order_book.bids)
        self.assertEqual(101, order_book.get_best_bid())
        self.assertEqual(volume, order_book.get_bid_volume_at_limit_price(order_price))

    def test_best_bid_ask_and_volume(self):
        order_book = OrderBook()
        orders = [
            {
                'type': 'limit',
                "price": 102,
                'qty': 2,
                'side': 'ask',
                'order_id': 1
            },
            {
                'type': 'limit',
                "price": 101,
                'qty': 5,
                'side': 'ask',
                'order_id': 2
            },
            {
                'type': 'limit',
                "price": 98,
                'qty': 10,
                'side': 'bid',
                'order_id': 3
            },
            {
                'type': 'limit',
                "price": 101,
                'qty': 2,
                'side': 'ask',
                'order_id': 4
            },
            {
                'type': 'limit',
                "price": 99,
                'qty': 7,
                'side': 'bid',
                'order_id': 5
            },
            {
                'type': 'limit',
                "price": 99,
                'qty': 9,
                'side': 'bid',
                'order_id': 6
            },
        ]
        for order in orders:
            order_book.parse_input(order)
        self.assertEqual(101, order_book.get_best_ask())
        self.assertEqual(99, order_book.get_best_bid())
        self.assertEqual(16, order_book.get_bid_volume_at_limit_price(99))
        self.assertEqual(7, order_book.get_ask_volume_at_limit_price(101))

    def test_cancel_not_only_order_at_price(self):
        """
        Cancel order which is not the only order at that price
        - check if order doesn't exist in order_id map
        - check if order doesn't exist in OrderList in corresponding price value
        - check volume at price is 0
        """
        order_book = OrderBook()
        orders = [
            {
                'type': 'limit',
                "price": 101,
                'qty': 2,
                'side': 'ask',
                'order_id': 1
            },
            {
                "type": 'cancel',
                'order_id': 1,
            }
        ]
        for order in orders:
            order_book.parse_input(order)
        order_id = 1
        order_price = 101
        self.assertNotIn(order_id, order_book.order_id_map)
        self.assertNotIn(order_price, order_book.asks)
        self.assertNotIn(order_price, order_book.ask_price_heap)
        with self.assertRaises(Exception):
            order_book.get_best_ask()
        self.assertEqual(0, order_book.get_ask_volume_at_limit_price(order_price))

    def test_cancel_only_order_at_price(self):
        """
        Cancel order and order is the only order at that price
        - check if order doesn't exist in order_id map
        - check if order doesn't exist in OrderList in corresponding price value
        - check volume has been updated
        """
        order_book = OrderBook()
        orders = [
            {
                'type': 'limit',
                "price": 101,
                'qty': 2,
                'side': 'ask',
                'order_id': 1
            },
            {
                'type': 'limit',
                "price": 101,
                'qty': 5,
                'side': 'ask',
                'order_id': 2
            },
            {
                'type': 'limit',
                "price": 101,
                'qty': 10,
                'side': 'ask',
                'order_id': 3
            },
            {
                "type": 'cancel',
                'order_id': 2,
            }
        ]
        for order in orders:
            order_book.parse_input(order)
        order_id = 2
        order_price = 101
        self.assertNotIn(order_id, order_book.order_id_map)
        self.assertEqual(10, order_book.asks[order_price].head.next.qty)
        self.assertEqual(12, order_book.get_ask_volume_at_limit_price(order_price))

    def test_execute_market_trade(self):
        """
        - check if trade exists in the trade tracker
        - check if best bid/ask order has been updated
        - check volume at previous bid/ask is 0
        """
        order_book = OrderBook()
        orders = [
            {
                'type': 'limit',
                "price": 101,
                'qty': 2,
                'side': 'ask',
                'order_id': 1
            },
            {
                'type': 'limit',
                "price": 99,
                'qty': 5,
                'side': 'bid',
                'order_id': 2
            },
            {
                'type': 'limit',
                "price": 102,
                'qty': 10,
                'side': 'ask',
                'order_id': 3
            },
            {
                "type": 'market',
                'side': 'bid',
            }
        ]
        for order in orders:
            order_book.parse_input(order)
        self.assertIn({'side': 'bid', 'price': 101, 'qty': 2}, order_book.trades)
        self.assertEqual(0, order_book.get_ask_volume_at_limit_price(101))
        self.assertEqual(102, order_book.get_best_ask())


if __name__ == '__main__':
    unittest.main()
