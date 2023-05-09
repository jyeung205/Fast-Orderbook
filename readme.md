# Fast Limit Orderbook

This is a fast limit orderbook implementation based on the post: 

https://web.archive.org/web/20110219163448/http://howtohft.wordpress.com/2011/02/15/how-to-build-a-fast-limit-order-book/

There are three main operations that a limit order book has to implement: add, cancel, and execute.  

The vast majority of the activity in a book is usually made up of add and cancel operations, distantly followed by executions in third. 

## Methods 

First, I created an Order object. Next, I created an OrderList object which is a doubly linked list of 
Order objects, arranged in the order the Orders were added to the orderbook. 
I then used a dict with the price as the key and OrderList object as the value.
Furthermore, I use a heap to keep track of the best bid/ask.

Each bid/ask side of the book is stored in its own dict to enable quick access to the best bid/ask. 

Here are the runtime complexities for the different methods implemented in this orderbook implementation:

#### place_limit_order()
- O(1) if price exists in orderbook
- O(logn) if price does not exist in orderbook (heappush)

#### cancel_order()
- O(1) if volume at price does not become 0
- O(n) if volume at price becomes 0 (remove price and reheapify)

#### execute_market_order()
- O(1) if volume at best bid/ask does not become 0
- O(logn) volume at best bid/ask becomes 0 (update best bid/ask using heappop)

#### get_best_bid()
- O(1)

#### get_best_ask()
- O(1)

#### get_volume_at_limit()
- O(1)

## Improvements:
- When executing a market order, this implementation can only execute 
against the oldest order at the best bid/ask, and does not consider the trade size of the market order.
- Limit orders which cross the bid/ask spread do not execute as a taker order, and are instead added to the orderbook.
