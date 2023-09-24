# Reinforce your trades with trades

`reinforce-trader` is an open-source trading journal app that provides a comprehensive solution for trader to track, analyse and improve their trading strategies. The best way to learn anything is to learn from your own mistakes. `reinforce-trader` aims to provide a solution for traders so that they can maintain a systematic approach to *"reinforce"* their trading strategies.

`reinforce-trader` emphasizes the use of technical pattarns when traders make trading decisions. Traders often use technical patterns to find entry points and exit points. e.g Drawing lines of resistance levels and supporting levels, Drawing a triangle pattern, ...etc. Therefore, `reinforce-traders` allows you to upload an image to capture the moment of trade. I personally use [TradingView](https://www.tradingview.com/) to draw lines and you can easily download the chart image using Tradingview's "Take a Snapshot" function.


## How to start
# 1. Make a copy of .env.sample and rename it as .env
```bash
cp .env.sample .env
```

# 2. Start with docker
```bash
# `docker compose up -d --build` if you want to rebuild it
docker compose up -d
```

# 3. Open the app
You can start adding new trades in your trading journal: [localhost:8050/add-trade](http://localhost:8050/add-trade)

## How to use
### Add a new trade
You can add a new trade on [localhost:8050/add-trade](http://localhost:8050/add-trade)

![add-trade.png](add-trade.png)

### View your trades
You then can view all your trades on [localhost:8050/trades](http://localhost:8050/trades)

Study the chart pattern

![trades-chart-pattern.png](trades-chart-pattern.png)

View the trade records

![trades-table.png](trades-table.png)


### (Coming soon) View your entry and exit points on the candlestick

