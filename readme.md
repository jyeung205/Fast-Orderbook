place_limit_order
- O(1) if price exists in orderbook
- O(logn) if price does not exist in orderbook

cancel_order
- O(1) if volume at price does not become 0
- O(logn) if volume at price becomes 0

execute_market_order
- O(1)
- O(logn) if have to update best bid/ask

get_best_bid
- O(1)

get_best_ask
- O(1)

get_volume_at_limit
- O(1)

Improvements:
Currently can only take market order to 
take best bid/ask without considering qty