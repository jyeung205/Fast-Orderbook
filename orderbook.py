
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

    def remove_head(self):
        self.volume -= self.head.qty
        if self.head is self.tail:  # if only one order in OrderList
            self.head = None
            self.tail = None
        else:
            self.head = self.head.next

    def print_orderlist(self):
        head_copy = self.head
        while head_copy is not None:
            print(f'{head_copy.bid_ask} order at price {self.price}, {head_copy.qty} qty')
            head_copy = head_copy.next


class Tree:
    def __init__(self):
        self.price_map = {}  # dict{price: OrderList object}
        self.order_map = {}  # dict{order_id: Order object}
        self.max_price = None
        self.min_price = None

    def add(self, order: Order):
        price = order.price
        # if self.max_price is not None:
        #     self.max_price = max(self.max_price, price)
        # else:
        #     self.max_price = price
        # if self.min_price is not None:
        #     self.min_price = min(self.min_price, price)
        # else:
        #     self.min_price = price
        self.order_map[order.order_id] = order
        if price in self.price_map:
            self.price_map[price].add_order(order)
        else:
            self.price_map[price] = OrderList(order)

    def cancel(self, order_id: int):
        order = self.order_map[order_id]
        self.price_map[order.price].remove_order(order)
        if self.price_map[order.price].volume == 0:
            del self.price_map[order.price]
            # self.update_min_max_price()
        del self.order_map[order_id]

    # def update_min_max_price(self):
    #     if len(self.price_map) == 0:
    #         self.min_price = None
    #         self.max_price = None
    #     else:
    #         self.min_price = min(self.price_map)
    #         self.max_price = max(self.price_map)

    def get_volume_at_limit(self, limit_price):
        return self.price_map[limit_price].volume

    def print_price_map(self):
        print("Price Map", self.price_map)

    def print_order_map(self):
        print("Order Map", self.order_map)


class OrderBook:
    def __init__(self):
        self.bids_tree = Tree()
        self.asks_tree = Tree()
        self.id_count = 1
        self.trades = []

    def parse_input(self, input):
        if input['type'] == 'limit':
            self.place_limit_order(input['price'], input['qty'], input['bid_ask'])
        elif input['type'] == 'cancel':
            if self.asks_tree.order_map.get(input['order_id']):
                self.cancel_ask_order(input['order_id'])
            elif self.bids_tree.order_map.get(input['order_id']):
                self.cancel_bid_order(input['order_id'])
            else:
                print(
                    f'Order id {input["order_id"]} does not exist in the orderbook! ----------------------------------')
        elif input['type'] == 'market':
            self.execute_market_order(input['bid_ask'])
        else:
            print('invalid input type')

    def place_limit_order(self, price, qty, bid_ask):
        order = Order(price, qty, bid_ask, order_id=self.id_count)
        if order.bid_ask == 'bid':
            self.bids_tree.add(order)
        else:
            self.asks_tree.add(order)
        self.id_count += 1

    def execute_market_order(self, bid_ask):  # todo market order with qty
        if bid_ask == 'bid':
            price = min(self.asks_tree.price_map)

            # price = self.asks_tree.min_price
            order_id = self.asks_tree.price_map[price].head.order_id
            qty = self.asks_tree.price_map[price].head.qty
            self.asks_tree.price_map[price].remove_head()
            del self.asks_tree.order_map[order_id]
            if self.asks_tree.price_map[price].volume == 0:
                del self.asks_tree.price_map[price]
            self.trades.append((bid_ask, price, qty))
            # self.asks_tree.update_min_max_price()
        else:
            # price = self.bids_tree.max_price
            price = max(self.bids_tree.price_map)
            order_id = self.bids_tree.price_map[price].head.order_id
            qty = self.bids_tree.price_map[price].head.qty
            self.bids_tree.price_map[price].remove_head()
            del self.bids_tree.order_map[order_id]
            if self.bids_tree.price_map[price].volume == 0:
                del self.bids_tree.price_map[price]
            self.trades.append((bid_ask, price, qty))
            # self.bids_tree.update_min_max_price()

    def cancel_bid_order(self, order_id):
        self.bids_tree.cancel(order_id)

    def cancel_ask_order(self, order_id):
        self.asks_tree.cancel(order_id)

    def get_best_bid(self):
        return self.bids_tree.max_price

    def get_best_ask(self):
        return self.asks_tree.min_price

    def get_bid_volume_at_limit_price(self, price):
        return self.bids_tree.get_volume_at_limit(limit_price=price)

    def get_ask_volume_at_limit_price(self, price):
        return self.asks_tree.get_volume_at_limit(limit_price=price)

    def print_bid_order_map(self):
        self.bids_tree.print_order_map()

    def print_ask_order_map(self):
        self.asks_tree.print_order_map()

    def print_bid_price_map(self):
        self.bids_tree.print_price_map()

    def print_ask_price_map(self):
        self.asks_tree.print_price_map()

    def print_orderbook(self):
        bids = []
        for price, orderlist in self.bids_tree.price_map.items():
            bids.append((price, orderlist.volume))
        asks = []
        for price, orderlist in self.asks_tree.price_map.items():
            asks.append((price, orderlist.volume))
        print('asks', asks)
        print(self.asks_tree.order_map)
        print('bids', bids)
        print(self.bids_tree.order_map)
        print('trades', self.trades)


# todo how to keep the price of the orders sort ??

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

    for input in inputs:
        orderbook.parse_input(input)

        orderbook.print_orderbook()
        # print('ASK ---------')
        # orderbook.print_ask_order_map()
        # orderbook.print_ask_price_map()
        # print('best ask', orderbook.get_best_ask())
        # print('BID ---------')
        # orderbook.print_bid_order_map()
        # orderbook.print_bid_price_map()
        # print('best bid', orderbook.get_best_bid())
        #
        # if input['type'] == 'limit':
        #     if input['bid_ask'] == 'bid':
        #         print('volume', orderbook.get_bid_volume_at_limit_price(input['price']))
        #     else:
        #         print('volume', orderbook.get_ask_volume_at_limit_price(input['price']))
        print('----------------------------------------------------')

    # tree = RBTree()
    # tree.insert()
