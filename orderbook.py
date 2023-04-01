import heapq

from sortedcontainers import SortedDict


class Order:

    def __init__(self, price, qty, bid_ask, order_id):
        self.price = price
        self.bid_ask = bid_ask
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

    def add_order(self, order: Order):
        self.volume += order.qty
        self.tail.next = order
        order.prev = self.tail
        self.tail = order

    def remove_order(self, order: Order):
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
            print(f'{head_copy.bid_ask} order at price {self.price}, {head_copy.qty} qty')
            head_copy = head_copy.next


class OrderBook:
    def __init__(self):
        self.order_id_map = {}
        self.bid_price_map = SortedDict()
        self.ask_price_map = SortedDict()
        self.trades = []
        self.bid_price_heap = []
        self.ask_price_heap = []

    def parse_input(self, input: dict):
        if input['type'] == 'limit':
            self.place_limit_order(input['price'], input['qty'], input['bid_ask'], input['order_id'])
        elif input['type'] == 'cancel':
            self.cancel_order(input['order_id'])
        elif input['type'] == 'market':
            self.execute_market_order(input['bid_ask'])
        else:
            raise Exception('Invalid input type, only accept limit, cancel, market')

    def place_limit_order(self, price: int, qty: int, bid_ask: str, order_id: int):
        order = Order(price, qty, bid_ask, order_id)
        self.order_id_map[order_id] = order
        if order.bid_ask == 'bid':
            if price in self.bid_price_map:
                order_list = self.bid_price_map[price]
                order_list.add_order(order)
            else:
                self.bid_price_map[price] = OrderList(order)
                heapq.heappush(self.bid_price_heap, -price)
        else:
            if price in self.ask_price_map:
                order_list = self.ask_price_map[price]
                order_list.add_order(order)
            else:
                self.ask_price_map[price] = OrderList(order)
                heapq.heappush(self.ask_price_heap, price)

    def cancel_order(self, order_id: int):
        try:
            order = self.order_id_map[order_id]
        except:
            raise Exception('Order id does not exist in the orderbook')
        price = order.price
        bid_ask = order.bid_ask
        if bid_ask == 'bid':
            order_list = self.bid_price_map[price]
            order_list.remove_order(order)
            if order_list.volume == 0:
                del self.bid_price_map[price]
                heapq.heappop(self.bid_price_heap)
        else:
            order_list = self.ask_price_map[price]
            order_list.remove_order(order)
            if order_list.volume == 0:
                del self.ask_price_map[price]
                heapq.heappop(self.ask_price_heap)
        del self.order_id_map[order_id]

    def execute_market_order(self, bid_ask: str):
        if bid_ask == 'bid':
            price = self.ask_price_heap[0]
            order_list = self.ask_price_map[price]

            best_maker_order = order_list.head
            maker_order_id = best_maker_order.order_id
            qty = best_maker_order.qty

            order_list.remove_order(best_maker_order)
            del self.order_id_map[maker_order_id]

            if order_list.volume == 0:
                del self.ask_price_map[price]
                heapq.heappop(self.ask_price_heap)

        else:
            price = -self.bid_price_heap[0]
            order_list = self.bid_price_map[price]

            best_maker_order = order_list.head
            maker_order_id = best_maker_order.order_id
            qty = best_maker_order.qty

            order_list.remove_order(best_maker_order)
            del self.order_id_map[maker_order_id]

            if order_list.volume == 0:
                del self.bid_price_map[price]
                heapq.heappop(self.bid_price_heap)

        self.trades.append((bid_ask, price, qty))

    def get_best_bid(self):
        try:
            return -self.bid_price_heap[0]
        except:
            raise Exception('There are no bid orders in the orderbook')

    def get_best_ask(self):
        try:
            self.ask_price_heap[0]
        except:
            raise Exception('There are no ask orders in the orderbook')

    def get_bid_volume_at_limit_price(self, price):
        try:
            return self.bid_price_map[price].volume
        except:
            return 0

    def get_ask_volume_at_limit_price(self, price):
        try:
            return self.ask_price_map[price].volume
        except:
            return 0

    def print_orderbook(self):
        bids = []
        for price, orderlist in self.bid_price_map.items():
            bids.append((price, orderlist.volume))
        asks = []
        for price, orderlist in self.ask_price_map.items():
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
            'bid_ask': 'ask',
            'order_id': 1
        },
        {
            'type': 'limit',
            "price": 99,
            'qty': 5,
            'bid_ask': 'bid',
            'order_id': 2
        },
        {
            'type': 'limit',
            "price": 99,
            'qty': 4,
            'bid_ask': 'bid',
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
            'bid_ask': 'ask',
            'order_id': 4
        },
        {
            'type': 'limit',
            "price": 102,
            'qty': 9,
            'bid_ask': 'ask',
            'order_id': 5
        },
        {
            "type": 'cancel',
            'order_id': 3,
        },
        {
            'type': 'market',
            'bid_ask': 'bid',
        },
        {
            'type': 'market',
            'bid_ask': 'ask',
        },
        {
            'type': 'market',
            'bid_ask': 'bid',
        },
    ]
    inputs = [
        {
            'type': 'limit',
            "price": 100,
            'qty': 10,
            'bid_ask': 'bid',
            'order_id': 1
        },
        {
            'type': 'limit',
            "price": 101,
            'qty': 19,
            'bid_ask': 'bid',
            'order_id': 2
        }
    ]
    for input in inputs:
        orderbook.parse_input(input)
        # orderbook.print_orderbook()
        print(orderbook.get_best_bid())
        print('----------------------------------------------------')
