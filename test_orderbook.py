import unittest
from orderbook import OrderBook, Order


class TestOrderBook(unittest.TestCase):
    def test_add_order(self):
        """
        - check if order exists in order_id map
        - check if order exists in OrderList in corresponding price value
        - check if best bid/ask has been updated
        """

        # Test adding a new order
        order_book = OrderBook()
        order = {
            'type': 'limit',
            "price": 100,
            'qty': 10,
            'bid_ask': 'bid',
            'order_id': 1
        },
        order_book.parse_input(order)

        self.assertEqual(order_id in order_book.order_map and order_book.order_map[order_id] == Order(order))
        # self.assertEqual(len(order_book.sell_orders), 0)

    def test_cancel_order(self):
        """
        - check if order doesn't exist in order_id map
        - check if order doesn't exist in OrderList in corresponding price value
        - check best bid/ask has been updated
        """
        # Test canceling an existing order
        order_book = OrderBook()
        orders = [
            {
                'type': 'limit',
                "price": 100,
                'qty': 10,
                'bid_ask': 'bid',
                'order_id': 1
            },
            {
                "type": 'cancel',
                'order_id': 1,
            },
        ]
        for order in orders:
            order_book.parse_input(order)
        # self.assertEqual(len(order_book.buy_orders), 0)

    def test_execute_market_trade(self):
        """
        - check if best bid/ask order has been removed
        - check if trade exists in the trade tracker
        """
        pass


if __name__ == '__main__':
    unittest.main()
