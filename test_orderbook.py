import unittest
from orderbook import OrderBook


class TestOrderBook(unittest.TestCase):
    def test_create_order(self):
        """
        - check if price exists in order_book.bids
        - check if order exists in order_id_map
        - check the priority/order of the OrderList
        - check volumes at each price are correct
        """
        inputs = [
            {
                'type': 'limit',
                "side": 'bid',
                'price': 99,
                'qty': 1,
                'order_id': 1
            },
            {
                'type': 'limit',
                "side": 'bid',
                'price': 99,
                'qty': 2,
                'order_id': 2
            },
            {
                'type': 'limit',
                "side": 'bid',
                'price': 100,
                'qty': 5,
                'order_id': 3
            },
            {
                'type': 'limit',
                "side": 'bid',
                'price': 99,
                'qty': 4,
                'order_id': 4
            },
        ]
        order_book = OrderBook()
        for input in inputs:
            order_book.parse_input(input)
        self.assertIn(99, order_book.bids)
        self.assertIn(100, order_book.bids)
        self.assertIn(1, order_book.order_id_map)
        self.assertIn(2, order_book.order_id_map)
        self.assertIn(3, order_book.order_id_map)
        self.assertIn(4, order_book.order_id_map)
        self.assertEqual(order_book.order_id_map[1], order_book.bids[99].head)
        self.assertEqual(order_book.order_id_map[2], order_book.bids[99].head.next, order_book.bids[99].tail.prev)
        self.assertEqual(order_book.order_id_map[3], order_book.bids[100].head, order_book.bids[100].tail)
        self.assertEqual(order_book.order_id_map[4], order_book.bids[99].head.next.next, order_book.bids[99].tail)
        self.assertEqual(7, order_book.get_bid_volume_at_price(99))
        self.assertEqual(5, order_book.get_bid_volume_at_price(100))

    def test_cancel_head_order(self):
        """
        Cancel top priority order
        - check if order doesn't exist in order_id map
        - check if OrderList priority has been updated
        - check volume has been updated
        """
        inputs = [
            {
                'type': 'limit',
                "side": 'bid',
                'price': 99,
                'qty': 1,
                'order_id': 1
            },
            {
                'type': 'limit',
                "side": 'bid',
                'price': 99,
                'qty': 2,
                'order_id': 2
            },
            {
                'type': 'limit',
                "side": 'bid',
                'price': 99,
                'qty': 5,
                'order_id': 3
            },
            {
                'type': 'cancel',
                'order_id': 1
            },
        ]
        order_book = OrderBook()
        for input in inputs:
            order_book.parse_input(input)
        self.assertIn(99, order_book.bids)
        self.assertNotIn(1, order_book.order_id_map)
        self.assertEqual(order_book.order_id_map[2], order_book.bids[99].head, order_book.bids[99].tail.prev)
        self.assertEqual(order_book.order_id_map[3], order_book.bids[99].head.next, order_book.bids[99].tail)
        self.assertEqual(7, order_book.get_bid_volume_at_price(99))

    def test_cancel_middle_order(self):
        """
        Cancel middle priority order
        - check if order doesn't exist in order_id map
        - check if OrderList priority has been updated
        - check volume has been updated
        """
        inputs = [
            {
                'type': 'limit',
                "side": 'bid',
                'price': 99,
                'qty': 1,
                'order_id': 1
            },
            {
                'type': 'limit',
                "side": 'bid',
                'price': 99,
                'qty': 2,
                'order_id': 2
            },
            {
                'type': 'limit',
                "side": 'bid',
                'price': 99,
                'qty': 5,
                'order_id': 3
            },
            {
                'type': 'cancel',
                'order_id': 2
            },
        ]
        order_book = OrderBook()
        for input in inputs:
            order_book.parse_input(input)
        self.assertIn(99, order_book.bids)
        self.assertNotIn(2, order_book.order_id_map)
        self.assertEqual(order_book.order_id_map[1], order_book.bids[99].head, order_book.bids[99].tail.prev)
        self.assertEqual(order_book.order_id_map[3], order_book.bids[99].head.next, order_book.bids[99].tail)
        self.assertEqual(6, order_book.get_bid_volume_at_price(99))

    def test_cancel_tail_order(self):
        """
        Cancel least priority order
        - check if order doesn't exist in order_id map
        - check if OrderList priority has been updated
        - check volume has been updated
        """
        inputs = [
            {
                'type': 'limit',
                "side": 'bid',
                'price': 99,
                'qty': 1,
                'order_id': 1
            },
            {
                'type': 'limit',
                "side": 'bid',
                'price': 99,
                'qty': 2,
                'order_id': 2
            },
            {
                'type': 'limit',
                "side": 'bid',
                'price': 99,
                'qty': 5,
                'order_id': 3
            },
            {
                'type': 'cancel',
                'order_id': 3
            },
        ]
        order_book = OrderBook()
        for input in inputs:
            order_book.parse_input(input)
        self.assertIn(99, order_book.bids)
        self.assertNotIn(3, order_book.order_id_map)
        self.assertEqual(order_book.order_id_map[1], order_book.bids[99].head, order_book.bids[99].tail.prev)
        self.assertEqual(order_book.order_id_map[2], order_book.bids[99].head.next, order_book.bids[99].tail)
        self.assertEqual(3, order_book.get_bid_volume_at_price(99))

    def test_cancel_only_order(self):
        """
        Cancel only order at price
        - check if order doesn't exist in order_id map
        - check if price has been deleted from order_book.bids
        - check volume at price is 0
        - check best bid has been updated
        """
        inputs = [
            {
                'type': 'limit',
                "side": 'bid',
                'price': 99,
                'qty': 5,
                'order_id': 1
            },
            {
                'type': 'limit',
                "side": 'bid',
                'price': 98,
                'qty': 3,
                'order_id': 2
            },
            {
                'type': 'cancel',
                'order_id': 1
            },
        ]
        order_book = OrderBook()
        for input in inputs:
            order_book.parse_input(input)
        self.assertNotIn(99, order_book.bids)
        self.assertNotIn(1, order_book.order_id_map)
        self.assertEqual(0, order_book.get_bid_volume_at_price(99))
        self.assertEqual(98, order_book.get_best_bid())

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
        self.assertEqual(0, order_book.get_ask_volume_at_price(101))
        self.assertEqual(102, order_book.get_best_ask())

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
        self.assertEqual(16, order_book.get_bid_volume_at_price(99))
        self.assertEqual(7, order_book.get_ask_volume_at_price(101))


if __name__ == '__main__':
    unittest.main()
