"""
Orderbook
attributes
- keep track of orders, separated by price
- prioritise orders that arrive earlier
- keep track of trades
- keep track of min/max bid/ask prices

methods
- add_order
- cancel_order
- execute_market_order
- get_best_bid/ask
- get_volume

ask = {price: LinkedList of Order objects}
bid = {price: LinkedList of Order objects}


LinkedListObject
- volume attribute
"""

import heapq

from sortedcontainers import SortedDict


class Order:

    def __init__(self, price, qty, side, order_id):
        self.price = price
        self.side = side
        self.qty = qty
        self.order_id = order_id
        self.prev = None
        self.next = None


class OrderList:
    """
    Linked list of Order objects
    """

    def __init__(self, order: Order):
        self.price = order.price
        self.volume = order.qty
        self.head = order
        self.tail = order

    def add(self, order: Order):
        self.volume += order.qty
        self.tail.next = order
        order.prev = self.tail
        self.tail = order

    def remove(self, order: Order):
        self.volume -= order.qty
        if self.head is order and self.tail is order:
            self.head = None
            self.tail = None
        elif self.head is order:
            order.next.prev = None
            self.head = order.next
        elif self.tail is order:
            order.prev.next = None
            self.tail = order.prev
        else:
            order.prev.next = order.next
            order.next.prev = order.prev

    def print_orderlist(self):
        head_copy = self.head
        while head_copy is not None:
            print(f'{head_copy.side} order at price {self.price}, {head_copy.qty} qty')
            head_copy = head_copy.next


class OrderBook:
    def __init__(self):
        self.order_id_map = {}
        self.bids = SortedDict()
        self.asks = SortedDict()
        self.trades = []
        self.bid_price_heap = []
        self.ask_price_heap = []

    def parse_input(self, input: dict):
        if input['type'] == 'limit':
            self.create_order(
                input['price'],
                input['qty'],
                input['side'],
                input['order_id']
            )
        elif input['type'] == 'cancel':
            self.cancel_order(input['order_id'])
        elif input['type'] == 'market':
            self.execute_market_order(input['side'])
        else:
            raise Exception('Invalid input type, only accept type: limit, cancel, market')

    def create_order(self, price: int, qty: int, side: str, order_id: int):
        order = Order(price, qty, side, order_id)
        self.order_id_map[order_id] = order
        if order.side == 'bid':
            if price in self.bids:
                order_list = self.bids[price]
                order_list.add(order)
            else:
                self.bids[price] = OrderList(order)
                heapq.heappush(self.bid_price_heap, -price)
        else:
            if price in self.asks:
                order_list = self.asks[price]
                order_list.add(order)
            else:
                self.asks[price] = OrderList(order)
                heapq.heappush(self.ask_price_heap, price)

    def cancel_order(self, order_id: int):
        try:
            order = self.order_id_map[order_id]
        except KeyError:
            raise Exception('Order id does not exist in the orderbook')
        price = order.price
        side = order.side
        if side == 'bid':
            order_list = self.bids[price]
            order_list.remove(order)
            if order_list.volume == 0:
                del self.bids[price]
                self.bid_price_heap.remove(-price)
                heapq.heapify(self.bid_price_heap)
        else:
            order_list = self.asks[price]
            order_list.remove(order)
            if order_list.volume == 0:
                del self.asks[price]
                self.ask_price_heap.remove(price)
                heapq.heapify(self.ask_price_heap)
        del self.order_id_map[order_id]

    def execute_market_order(self, side: str):
        if side == 'bid':
            price = self.ask_price_heap[0]
            order_list = self.asks[price]

            best_maker_order = order_list.head
            maker_order_id = best_maker_order.order_id
            qty = best_maker_order.qty

            order_list.remove(best_maker_order)
            del self.order_id_map[maker_order_id]

            if order_list.volume == 0:
                del self.asks[price]
                heapq.heappop(self.ask_price_heap)

        else:
            price = -self.bid_price_heap[0]
            order_list = self.bids[price]

            best_maker_order = order_list.head
            maker_order_id = best_maker_order.order_id
            qty = best_maker_order.qty

            order_list.remove(best_maker_order)
            del self.order_id_map[maker_order_id]

            if order_list.volume == 0:
                del self.bids[price]
                heapq.heappop(self.bid_price_heap)

        self.trades.append({
            "side": side,
            "price": price,
            "qty": qty
        })

    def get_best_bid(self):
        try:
            return -self.bid_price_heap[0]
        except IndexError:
            print('There are no bid orders in the orderbook')

    def get_best_ask(self):
        try:
            return self.ask_price_heap[0]
        except IndexError:
            print('There are no ask orders in the orderbook')

    def get_bid_volume_at_price(self, price: int):
        try:
            return self.bids[price].volume
        except KeyError:
            return 0

    def get_ask_volume_at_price(self, price: int):
        try:
            return self.asks[price].volume
        except KeyError:
            return 0

    def print_orderbook(self):
        bids = []
        for price, orderlist in self.bids.items():
            bids.append((price, orderlist.volume))
        asks = []
        for price, orderlist in self.asks.items():
            asks.append((price, orderlist.volume))
        print('asks', asks)
        print('bids', bids)
        print('order id map ', self.order_id_map)
        print('trades', self.trades)


if __name__ == '__main__':
    orderbook = OrderBook()
    inputs = [
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
            "price": 99,
            'qty': 4,
            'side': 'bid',
            'order_id': 3
        },
        {
            "type": 'cancel',
            'order_id': 1,
        },
        {
            'type': 'limit',
            "price": 101,
            'qty': 5,
            'side': 'ask',
            'order_id': 4
        },
        {
            'type': 'limit',
            "price": 102,
            'qty': 9,
            'side': 'ask',
            'order_id': 5
        },
        {
            "type": 'cancel',
            'order_id': 3,
        },
        {
            'type': 'market',
            'side': 'bid',
        },
        {
            'type': 'market',
            'side': 'ask',
        },
        {
            'type': 'market',
            'side': 'bid',
        },
    ]
    for input in inputs:
        orderbook.parse_input(input)
        orderbook.print_orderbook()
        print('----------------------------------------------------')
