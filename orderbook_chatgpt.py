class Order:
    def __init__(self, idNumber, buyOrSell, shares, limit):
        self.idNumber = idNumber
        self.buyOrSell = buyOrSell
        self.shares = shares
        self.limit = limit
        self.entryTime = None
        self.eventTime = None
        self.nextOrder = None
        self.prevOrder = None
        self.parentLimit = None


class Limit:
    def __init__(self, limitPrice):
        self.limitPrice = limitPrice
        self.size = 0
        self.totalVolume = 0
        self.parent = None
        self.leftChild = None
        self.rightChild = None
        self.headOrder = None
        self.tailOrder = None


class Book:
    def __init__(self):
        self.buyTree = None
        self.sellTree = None
        self.lowestSell = None
        self.highestBuy = None

    def add(self, order):
        limit = None
        tree = None
        if order.buyOrSell:
            tree = self.buyTree
        else:
            tree = self.sellTree

        if tree is None:
            limit = Limit(order.limit)
            limit.parent = None
            tree = limit
        else:
            limit = self.findLimit(order.limit, tree)
            if limit is None:
                limit = Limit(order.limit)
                self.insertLimit(limit, tree)
        self.insertOrder(order, limit)

    def cancel(self, order):
        if order.parentLimit is None:
            return

        limit = order.parentLimit
        if order.nextOrder is not None:
            order.nextOrder.prevOrder = order.prevOrder
        else:
            limit.tailOrder = order.prevOrder

        if order.prevOrder is not None:
            order.prevOrder.nextOrder = order.nextOrder
        else:
            limit.headOrder = order.nextOrder

        limit.size -= 1
        limit.totalVolume -= order.shares
        order.parentLimit = None

    def execute(self, order):
        if order.parentLimit is None:
            return

        self.cancel(order)
        if order.buyOrSell:
            self.highestBuy = self.getHighestBuy()
        else:
            self.lowestSell = self.getLowestSell()

    def getVolumeAtLimit(self, limitPrice):
        limit = self.findLimit(limitPrice, self.buyTree)
        if limit is None:
            limit = self.findLimit(limitPrice, self.sellTree)
        if limit is None:
            return 0
        return limit.totalVolume

    def getBestBid(self):
        if self.highestBuy is None:
            return None
        return self.highestBuy.limitPrice

    def getBestOffer(self):
        if self.lowestSell is None:
            return None
        return self.lowestSell.limitPrice

    def findLimit(self, limitPrice, limit):
        if limit is None:
            return None
        if limitPrice == limit.limitPrice:
            return limit
        elif limitPrice < limit.limitPrice:
            return self.findLimit(limitPrice, limit.leftChild)
        else:
            return self.findLimit(limitPrice, limit.rightChild)

    def insertLimit(self, limit, tree):
        if limit.limitPrice < tree.limitPrice:
            if tree.leftChild is None:
                tree.leftChild = limit
                limit.parent = tree
            else:
                self.insertLimit(limit, tree.leftChild)
        elif limit.limitPrice > tree.limitPrice:
            if tree.rightChild is None:
                tree.rightChild = limit
                limit.parent = tree
            else:
                self.insertLimit(limit, tree.rightChild)
        else:
            raise ValueError("Limit already exists in the order book")

    def insertOrder(self, order, limit):
        if limit.headOrder is None:  # empty list
            limit.headOrder = order
            limit.tailOrder = order
        else:
            if order.buyOrSell and order.limit >= limit.tailOrder.limit:
                # new highest buy order, add to end of list
                order.prevOrder = limit.tailOrder
                limit.tailOrder.nextOrder = order
                limit.tailOrder = order
            elif not order.buyOrSell and order.limit <= limit.headOrder.limit:
                # new lowest sell order, add to front of list
                order.nextOrder = limit.headOrder
                limit.headOrder.prevOrder = order
                limit.headOrder = order
            else:
                # insert order in correct position based on price/time priority
                currOrder = limit.headOrder
                while currOrder is not None:
                    if (order.buyOrSell and order.limit >= currOrder.limit) or \
                            (not order.buyOrSell and order.limit <= currOrder.limit):
                        # insert order before current order
                        order.prevOrder = currOrder.prevOrder
                        order.nextOrder = currOrder
                        if currOrder.prevOrder is not None:
                            currOrder.prevOrder.nextOrder = order
                        else:
                            limit.headOrder = order
                        currOrder.prevOrder = order
                        break
                    currOrder = currOrder.nextOrder
        limit.size += 1
        limit.totalVolume += order.shares
        order.parentLimit = limit

    def print_tree(self):
        def dfs(node):
            dfs(node.leftChild)
            print(node.limitPrice)
            print(node.size)
            print(node.totalVolume)
            dfs(node.rightChild)
        dfs(self.buyTree)


if __name__ == '__main__':
    book = Book()
    order1 = Order(
        idNumber=1,
        buyOrSell=True,
        shares=1,
        limit=100
    )
    book.add(order1)
    order2 = Order(
        idNumber=1,
        buyOrSell=True,
        shares=1,
        limit=101
    )
    order3 = Order(
        idNumber=1,
        buyOrSell=True,
        shares=1,
        limit=103
    )
    book.add(order2)
    book.add(order3)

    book.print_tree()