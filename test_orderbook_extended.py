import unittest
from orderbook import OrderBook, OrderList, Order


class TestOrderListDirect(unittest.TestCase):
    """Direct unit tests for the OrderList doubly-linked list."""

    def test_init_single_order(self):
        order = Order(100, 5, 'bid', 1)
        ol = OrderList(order)
        self.assertEqual(ol.price, 100)
        self.assertEqual(ol.volume, 5)
        self.assertIs(ol.head, order)
        self.assertIs(ol.tail, order)

    def test_add_multiple_orders(self):
        o1 = Order(100, 5, 'bid', 1)
        o2 = Order(100, 3, 'bid', 2)
        o3 = Order(100, 7, 'bid', 3)
        ol = OrderList(o1)
        ol.add(o2)
        ol.add(o3)
        self.assertEqual(ol.volume, 15)
        self.assertIs(ol.head, o1)
        self.assertIs(ol.tail, o3)
        self.assertIs(o1.next, o2)
        self.assertIs(o2.prev, o1)
        self.assertIs(o2.next, o3)
        self.assertIs(o3.prev, o2)
        self.assertIsNone(o1.prev)
        self.assertIsNone(o3.next)

    def test_remove_head(self):
        o1 = Order(100, 5, 'bid', 1)
        o2 = Order(100, 3, 'bid', 2)
        ol = OrderList(o1)
        ol.add(o2)
        ol.remove(o1)
        self.assertEqual(ol.volume, 3)
        self.assertIs(ol.head, o2)
        self.assertIs(ol.tail, o2)
        self.assertIsNone(o2.prev)

    def test_remove_tail(self):
        o1 = Order(100, 5, 'bid', 1)
        o2 = Order(100, 3, 'bid', 2)
        ol = OrderList(o1)
        ol.add(o2)
        ol.remove(o2)
        self.assertEqual(ol.volume, 5)
        self.assertIs(ol.head, o1)
        self.assertIs(ol.tail, o1)
        self.assertIsNone(o1.next)

    def test_remove_middle(self):
        o1 = Order(100, 5, 'bid', 1)
        o2 = Order(100, 3, 'bid', 2)
        o3 = Order(100, 7, 'bid', 3)
        ol = OrderList(o1)
        ol.add(o2)
        ol.add(o3)
        ol.remove(o2)
        self.assertEqual(ol.volume, 12)
        self.assertIs(ol.head, o1)
        self.assertIs(ol.tail, o3)
        self.assertIs(o1.next, o3)
        self.assertIs(o3.prev, o1)

    def test_remove_only_order(self):
        o1 = Order(100, 5, 'bid', 1)
        ol = OrderList(o1)
        ol.remove(o1)
        self.assertEqual(ol.volume, 0)
        self.assertIsNone(ol.head)
        self.assertIsNone(ol.tail)


class TestAskSideOrders(unittest.TestCase):
    """Tests for ask-side order creation and cancellation, mirroring existing bid tests."""

    def test_create_ask_orders(self):
        ob = OrderBook()
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 101, 'qty': 3, 'order_id': 1})
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 101, 'qty': 5, 'order_id': 2})
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 102, 'qty': 7, 'order_id': 3})
        self.assertIn(101, ob.asks)
        self.assertIn(102, ob.asks)
        self.assertIn(1, ob.order_id_map)
        self.assertIn(2, ob.order_id_map)
        self.assertIn(3, ob.order_id_map)
        self.assertEqual(ob.order_id_map[1], ob.asks[101].head)
        self.assertEqual(ob.order_id_map[2], ob.asks[101].tail)
        self.assertEqual(8, ob.get_ask_volume_at_price(101))
        self.assertEqual(7, ob.get_ask_volume_at_price(102))

    def test_cancel_ask_head_order(self):
        ob = OrderBook()
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 101, 'qty': 3, 'order_id': 1})
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 101, 'qty': 5, 'order_id': 2})
        ob.parse_input({'type': 'cancel', 'order_id': 1})
        self.assertNotIn(1, ob.order_id_map)
        self.assertIn(101, ob.asks)
        self.assertIs(ob.asks[101].head, ob.order_id_map[2])
        self.assertEqual(5, ob.get_ask_volume_at_price(101))

    def test_cancel_ask_tail_order(self):
        ob = OrderBook()
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 101, 'qty': 3, 'order_id': 1})
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 101, 'qty': 5, 'order_id': 2})
        ob.parse_input({'type': 'cancel', 'order_id': 2})
        self.assertNotIn(2, ob.order_id_map)
        self.assertIn(101, ob.asks)
        self.assertIs(ob.asks[101].tail, ob.order_id_map[1])
        self.assertEqual(3, ob.get_ask_volume_at_price(101))

    def test_cancel_only_ask_order(self):
        ob = OrderBook()
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 101, 'qty': 3, 'order_id': 1})
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 102, 'qty': 5, 'order_id': 2})
        ob.parse_input({'type': 'cancel', 'order_id': 1})
        self.assertNotIn(101, ob.asks)
        self.assertNotIn(1, ob.order_id_map)
        self.assertEqual(0, ob.get_ask_volume_at_price(101))
        self.assertEqual(102, ob.get_best_ask())


class TestMarketOrderSellSide(unittest.TestCase):
    """Tests for market sell orders (side='ask'), executing against best bid."""

    def test_market_sell_executes_against_best_bid(self):
        ob = OrderBook()
        ob.parse_input({'type': 'limit', 'side': 'bid', 'price': 99, 'qty': 10, 'order_id': 1})
        ob.parse_input({'type': 'limit', 'side': 'bid', 'price': 98, 'qty': 5, 'order_id': 2})
        ob.parse_input({'type': 'market', 'side': 'ask'})
        self.assertIn({'side': 'ask', 'price': 99, 'qty': 10}, ob.trades)
        self.assertEqual(0, ob.get_bid_volume_at_price(99))
        self.assertEqual(98, ob.get_best_bid())

    def test_market_sell_leaves_remaining_orders_at_price(self):
        ob = OrderBook()
        ob.parse_input({'type': 'limit', 'side': 'bid', 'price': 99, 'qty': 3, 'order_id': 1})
        ob.parse_input({'type': 'limit', 'side': 'bid', 'price': 99, 'qty': 7, 'order_id': 2})
        ob.parse_input({'type': 'market', 'side': 'ask'})
        self.assertIn({'side': 'ask', 'price': 99, 'qty': 3}, ob.trades)
        self.assertEqual(7, ob.get_bid_volume_at_price(99))
        self.assertEqual(99, ob.get_best_bid())
        self.assertIn(99, ob.bids)
        self.assertIs(ob.bids[99].head, ob.order_id_map[2])


class TestMarketOrderRemainingAtPrice(unittest.TestCase):
    """Test that market orders leave remaining orders at the same price level intact."""

    def test_market_buy_leaves_remaining_asks(self):
        ob = OrderBook()
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 101, 'qty': 2, 'order_id': 1})
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 101, 'qty': 8, 'order_id': 2})
        ob.parse_input({'type': 'market', 'side': 'bid'})
        self.assertIn({'side': 'bid', 'price': 101, 'qty': 2}, ob.trades)
        self.assertEqual(8, ob.get_ask_volume_at_price(101))
        self.assertEqual(101, ob.get_best_ask())
        self.assertIn(101, ob.asks)
        self.assertIs(ob.asks[101].head, ob.order_id_map[2])


class TestMultipleMarketOrders(unittest.TestCase):
    """Tests for sequential market orders draining price levels."""

    def test_multiple_market_buys_drain_price_level(self):
        ob = OrderBook()
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 101, 'qty': 3, 'order_id': 1})
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 101, 'qty': 5, 'order_id': 2})
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 102, 'qty': 10, 'order_id': 3})
        ob.parse_input({'type': 'market', 'side': 'bid'})
        ob.parse_input({'type': 'market', 'side': 'bid'})
        self.assertEqual(len(ob.trades), 2)
        self.assertEqual(0, ob.get_ask_volume_at_price(101))
        self.assertEqual(102, ob.get_best_ask())

    def test_market_orders_across_price_levels(self):
        ob = OrderBook()
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 101, 'qty': 3, 'order_id': 1})
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 102, 'qty': 5, 'order_id': 2})
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 103, 'qty': 7, 'order_id': 3})
        ob.parse_input({'type': 'market', 'side': 'bid'})
        ob.parse_input({'type': 'market', 'side': 'bid'})
        self.assertEqual(ob.trades[0], {'side': 'bid', 'price': 101, 'qty': 3})
        self.assertEqual(ob.trades[1], {'side': 'bid', 'price': 102, 'qty': 5})
        self.assertEqual(103, ob.get_best_ask())
        self.assertNotIn(101, ob.asks)
        self.assertNotIn(102, ob.asks)


class TestErrorHandling(unittest.TestCase):
    """Tests for error conditions and edge cases."""

    def test_cancel_nonexistent_order_raises(self):
        ob = OrderBook()
        with self.assertRaises(Exception) as ctx:
            ob.parse_input({'type': 'cancel', 'order_id': 999})
        self.assertIn('Order id does not exist', str(ctx.exception))

    def test_invalid_input_type_raises(self):
        ob = OrderBook()
        with self.assertRaises(Exception) as ctx:
            ob.parse_input({'type': 'invalid'})
        self.assertIn('Invalid input type', str(ctx.exception))

    def test_market_order_on_empty_ask_side_raises(self):
        ob = OrderBook()
        with self.assertRaises(IndexError):
            ob.parse_input({'type': 'market', 'side': 'bid'})

    def test_market_order_on_empty_bid_side_raises(self):
        ob = OrderBook()
        with self.assertRaises(IndexError):
            ob.parse_input({'type': 'market', 'side': 'ask'})


class TestEmptyOrderBook(unittest.TestCase):
    """Tests for operations on a freshly initialized empty orderbook."""

    def test_best_bid_empty(self):
        ob = OrderBook()
        self.assertIsNone(ob.get_best_bid())

    def test_best_ask_empty(self):
        ob = OrderBook()
        self.assertIsNone(ob.get_best_ask())

    def test_volume_at_nonexistent_price(self):
        ob = OrderBook()
        self.assertEqual(0, ob.get_bid_volume_at_price(100))
        self.assertEqual(0, ob.get_ask_volume_at_price(100))

    def test_empty_orderbook_state(self):
        ob = OrderBook()
        self.assertEqual(len(ob.order_id_map), 0)
        self.assertEqual(len(ob.bids), 0)
        self.assertEqual(len(ob.asks), 0)
        self.assertEqual(len(ob.trades), 0)


class TestHeapIntegrity(unittest.TestCase):
    """Tests that best bid/ask heap tracking remains correct through complex operations."""

    def test_best_bid_after_multiple_insertions_and_cancellations(self):
        ob = OrderBook()
        ob.parse_input({'type': 'limit', 'side': 'bid', 'price': 95, 'qty': 1, 'order_id': 1})
        ob.parse_input({'type': 'limit', 'side': 'bid', 'price': 99, 'qty': 1, 'order_id': 2})
        ob.parse_input({'type': 'limit', 'side': 'bid', 'price': 97, 'qty': 1, 'order_id': 3})
        self.assertEqual(99, ob.get_best_bid())

        ob.parse_input({'type': 'cancel', 'order_id': 2})
        self.assertEqual(97, ob.get_best_bid())

        ob.parse_input({'type': 'cancel', 'order_id': 3})
        self.assertEqual(95, ob.get_best_bid())

        ob.parse_input({'type': 'cancel', 'order_id': 1})
        self.assertIsNone(ob.get_best_bid())

    def test_best_ask_after_multiple_insertions_and_cancellations(self):
        ob = OrderBook()
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 105, 'qty': 1, 'order_id': 1})
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 101, 'qty': 1, 'order_id': 2})
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 103, 'qty': 1, 'order_id': 3})
        self.assertEqual(101, ob.get_best_ask())

        ob.parse_input({'type': 'cancel', 'order_id': 2})
        self.assertEqual(103, ob.get_best_ask())

        ob.parse_input({'type': 'cancel', 'order_id': 3})
        self.assertEqual(105, ob.get_best_ask())

        ob.parse_input({'type': 'cancel', 'order_id': 1})
        self.assertIsNone(ob.get_best_ask())

    def test_best_bid_after_market_orders(self):
        ob = OrderBook()
        ob.parse_input({'type': 'limit', 'side': 'bid', 'price': 99, 'qty': 5, 'order_id': 1})
        ob.parse_input({'type': 'limit', 'side': 'bid', 'price': 98, 'qty': 3, 'order_id': 2})
        ob.parse_input({'type': 'limit', 'side': 'bid', 'price': 97, 'qty': 7, 'order_id': 3})
        self.assertEqual(99, ob.get_best_bid())

        ob.parse_input({'type': 'market', 'side': 'ask'})
        self.assertEqual(98, ob.get_best_bid())

        ob.parse_input({'type': 'market', 'side': 'ask'})
        self.assertEqual(97, ob.get_best_bid())

    def test_best_ask_after_market_orders(self):
        ob = OrderBook()
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 101, 'qty': 5, 'order_id': 1})
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 102, 'qty': 3, 'order_id': 2})
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 103, 'qty': 7, 'order_id': 3})
        self.assertEqual(101, ob.get_best_ask())

        ob.parse_input({'type': 'market', 'side': 'bid'})
        self.assertEqual(102, ob.get_best_ask())

        ob.parse_input({'type': 'market', 'side': 'bid'})
        self.assertEqual(103, ob.get_best_ask())


class TestMixedOperations(unittest.TestCase):
    """Tests combining multiple operation types in realistic sequences."""

    def test_add_cancel_market_sequence(self):
        ob = OrderBook()
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 101, 'qty': 2, 'order_id': 1})
        ob.parse_input({'type': 'limit', 'side': 'bid', 'price': 99, 'qty': 5, 'order_id': 2})
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 101, 'qty': 3, 'order_id': 3})
        ob.parse_input({'type': 'cancel', 'order_id': 1})
        self.assertEqual(3, ob.get_ask_volume_at_price(101))
        ob.parse_input({'type': 'market', 'side': 'bid'})
        self.assertIn({'side': 'bid', 'price': 101, 'qty': 3}, ob.trades)
        self.assertNotIn(101, ob.asks)

    def test_cancel_then_readd_at_same_price(self):
        ob = OrderBook()
        ob.parse_input({'type': 'limit', 'side': 'bid', 'price': 99, 'qty': 5, 'order_id': 1})
        ob.parse_input({'type': 'cancel', 'order_id': 1})
        self.assertNotIn(99, ob.bids)
        ob.parse_input({'type': 'limit', 'side': 'bid', 'price': 99, 'qty': 10, 'order_id': 2})
        self.assertIn(99, ob.bids)
        self.assertEqual(10, ob.get_bid_volume_at_price(99))
        self.assertEqual(99, ob.get_best_bid())

    def test_interleaved_bids_and_asks(self):
        ob = OrderBook()
        ob.parse_input({'type': 'limit', 'side': 'bid', 'price': 99, 'qty': 5, 'order_id': 1})
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 101, 'qty': 3, 'order_id': 2})
        ob.parse_input({'type': 'limit', 'side': 'bid', 'price': 98, 'qty': 7, 'order_id': 3})
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 102, 'qty': 4, 'order_id': 4})
        self.assertEqual(99, ob.get_best_bid())
        self.assertEqual(101, ob.get_best_ask())
        self.assertEqual(5, ob.get_bid_volume_at_price(99))
        self.assertEqual(7, ob.get_bid_volume_at_price(98))
        self.assertEqual(3, ob.get_ask_volume_at_price(101))
        self.assertEqual(4, ob.get_ask_volume_at_price(102))


class TestScaleAndStress(unittest.TestCase):
    """Tests with larger numbers of orders to verify data structure integrity."""

    def test_many_price_levels(self):
        ob = OrderBook()
        for i in range(1, 51):
            ob.parse_input({'type': 'limit', 'side': 'bid', 'price': i, 'qty': i, 'order_id': i})
        for i in range(51, 101):
            ob.parse_input({'type': 'limit', 'side': 'ask', 'price': i, 'qty': i, 'order_id': i})
        self.assertEqual(50, ob.get_best_bid())
        self.assertEqual(51, ob.get_best_ask())
        self.assertEqual(len(ob.order_id_map), 100)

    def test_many_orders_at_same_price(self):
        ob = OrderBook()
        total_qty = 0
        for i in range(1, 101):
            ob.parse_input({'type': 'limit', 'side': 'bid', 'price': 100, 'qty': i, 'order_id': i})
            total_qty += i
        self.assertEqual(total_qty, ob.get_bid_volume_at_price(100))
        self.assertIs(ob.bids[100].head, ob.order_id_map[1])
        self.assertIs(ob.bids[100].tail, ob.order_id_map[100])

    def test_cancel_all_orders(self):
        ob = OrderBook()
        for i in range(1, 21):
            ob.parse_input({'type': 'limit', 'side': 'bid', 'price': 90 + (i % 5), 'qty': 1, 'order_id': i})
        for i in range(1, 21):
            ob.parse_input({'type': 'cancel', 'order_id': i})
        self.assertEqual(len(ob.order_id_map), 0)
        self.assertEqual(len(ob.bids), 0)
        self.assertIsNone(ob.get_best_bid())

    def test_sequential_market_orders_drain_book(self):
        ob = OrderBook()
        for i in range(1, 11):
            ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 100 + i, 'qty': 1, 'order_id': i})
        for _ in range(10):
            ob.parse_input({'type': 'market', 'side': 'bid'})
        self.assertEqual(len(ob.trades), 10)
        self.assertEqual(len(ob.asks), 0)
        self.assertIsNone(ob.get_best_ask())
        # Verify trades were executed in price order (best ask first)
        for j in range(10):
            self.assertEqual(ob.trades[j]['price'], 101 + j)


class TestFIFOPriority(unittest.TestCase):
    """Tests that FIFO order priority is maintained correctly."""

    def test_market_order_takes_oldest_order_first(self):
        ob = OrderBook()
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 101, 'qty': 1, 'order_id': 1})
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 101, 'qty': 2, 'order_id': 2})
        ob.parse_input({'type': 'limit', 'side': 'ask', 'price': 101, 'qty': 3, 'order_id': 3})
        ob.parse_input({'type': 'market', 'side': 'bid'})
        self.assertEqual(ob.trades[0], {'side': 'bid', 'price': 101, 'qty': 1})
        self.assertNotIn(1, ob.order_id_map)
        self.assertIn(2, ob.order_id_map)
        self.assertIn(3, ob.order_id_map)
        self.assertIs(ob.asks[101].head, ob.order_id_map[2])

    def test_sequential_market_orders_respect_fifo(self):
        ob = OrderBook()
        ob.parse_input({'type': 'limit', 'side': 'bid', 'price': 99, 'qty': 10, 'order_id': 1})
        ob.parse_input({'type': 'limit', 'side': 'bid', 'price': 99, 'qty': 20, 'order_id': 2})
        ob.parse_input({'type': 'limit', 'side': 'bid', 'price': 99, 'qty': 30, 'order_id': 3})
        ob.parse_input({'type': 'market', 'side': 'ask'})
        ob.parse_input({'type': 'market', 'side': 'ask'})
        self.assertEqual(ob.trades[0], {'side': 'ask', 'price': 99, 'qty': 10})
        self.assertEqual(ob.trades[1], {'side': 'ask', 'price': 99, 'qty': 20})
        self.assertNotIn(1, ob.order_id_map)
        self.assertNotIn(2, ob.order_id_map)
        self.assertIn(3, ob.order_id_map)
        self.assertEqual(30, ob.get_bid_volume_at_price(99))


if __name__ == '__main__':
    unittest.main()
