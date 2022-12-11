a = 1070044.53
proc = 3

buy_price = a + ((a + proc) / 100)
sell_price = a - ((a + proc) / 100)

print(buy_price, sell_price)