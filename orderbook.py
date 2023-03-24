class Order:
    price = None
    bid_ask = None
    qty = None
    prev = None
    next = None
    order_id = None

    def __init__(self, price, qty, bid_ask, order_id):
        self.price = price
        self.bid_ask = bid_ask
        self.qty = qty
        self.order_id = order_id


class OrderList:
    """
    Linked list of Order objects
    """
    price = None
    volume = None
    head = None
    tail = None

    def __init__(self, order):
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
        if self.head is order:
            order.next.prev = None
            self.head = order.next
        elif self.tail is order:
            order.prev.next = None
            self.tail = order.prev
        else:
            order.prev.next = order.next
            order.next.prev = order.prev

    def print(self):
        head_copy = self.head
        while head_copy is not None:
            print(f'order at price{self.price} ', head_copy.bid_ask, head_copy.qty)
            head_copy = head_copy.next


class Tree:
    price_map = {}  # dict{price: OrderList object}
    order_map = {}  # dict{order_id: Order object}
    max_price = -999
    min_price = 999

    def add(self, order: Order):
        """
        Add Order to OrderList with corresponding price
        :param order:
        :return:
        """
        price = order.price
        self.max_price = max(self.max_price, price)
        self.min_price = max(self.min_price, price)
        bid_ask = order.bid_ask
        qty = order.qty
        self.order_map[order.order_id] = order
        if price in self.price_map:
            self.price_map[price].add(order)
        else:
            self.price_map[price] = OrderList(order)

    def cancel(self, order_id: int):
        order = self.order_map[order_id]
        self.price_map[order.price].remove(order)

    def get_volume_at_limit(self, limit_price):
        return self.price_map[limit_price].volume


class OrderBook:
    bids_tree = Tree()
    asks_tree = Tree()
    id_count = 1

    def parse_inputs(self, inputs):
        for input in inputs:
            if input['type'] == 'order':
                self.place_order(input['price'], input['qty'], input['bid_ask'])
            elif input['type'] == 'cancel':
                self.cancel_order(input['order_id'])
            else:
                pass
            print('bids', self.print_bid_orders())
            print('asks', self.print_ask_orders())

    def place_order(self, price, qty, bid_ask):
        # check if price bid lifts asks
        if bid_ask == 'bid' and price >= self.asks_tree.min_price:
            pass

        order = Order(price, qty, bid_ask, order_id=self.id_count)
        if order.bid_ask == 'bid':
            self.bids_tree.add(order)
        else:
            self.asks_tree.add(order)
        self.id_count += 1

    def cancel_order(self, order_id):
        self.bids_tree.cancel(order_id)

    def get_best_bid(self):
        return self.bids_tree.max_price

    def get_best_ask(self):
        return self.asks_tree.min_price

    def get_volume_at_limit_price(self, price):
        return self.bids_tree.get_volume_at_limit(limit_price=price)

    def print_bid_orders(self):
        print(self.bids_tree.price_map)
        for price, orderlist in self.bids_tree.price_map.items():
            orderlist.print()

    def print_ask_orders(self):
        print(self.asks_tree.price_map)
        for price, orderlist in self.asks_tree.price_map.items():
            orderlist.print()

    def print_all_orders(self):
        print(self.bids_tree.order_map)


if __name__ == '__main__':
    orderbook = OrderBook()
    inputs = [
        {
            'type': 'order',
            "price": 101,
            'qty': 1,
            'bid_ask': 'bid'
        },
        {
            'type': 'order',
            "price": 101,
            'qty': 2,
            'bid_ask': 'bid'
        },
        {
            "type": 'cancel',
            'order_id': 1,
        },
        {
            'type': 'order',
            "price": 101,
            'qty': 3,
            'bid_ask': 'bid'
        },
        {
            'type': 'order',
            "price": 101,
            'qty': 5,
            'bid_ask': 'bid'
        },
        {
            'type': 'order',
            "price": 100,
            'qty': 5,
            'bid_ask': 'bid'
        },
        {
            'type': 'order',
            "price": 100,
            'qty': 19,
            'bid_ask': 'bid'
        },
        {
            'type': 'order',
            "price": 101,
            'qty': 5,
            'bid_ask': 'bid'
        },

    ]
    orderbook.parse_inputs(inputs)
    # orderbook.print_bid_orders()
    # orderbook.print_all_orders()
    # # orderbook.cancel_order(3)
    # orderbook.print_bid_orders()
    # # orderbook.cancel_order(1)
    # orderbook.print_bid_orders()
    # orderbook.cancel_order(5)
    # orderbook.print_bid_orders()

