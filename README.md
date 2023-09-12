# Reinforce your trades with trades


`reinforce-trader` is an open-source trading journal app that provides a comprehensive solution for trader to track, analyse and improve their trading strategies. The best way to learn anything is to learn from your onw mistakes. `reinforce-trader` aims to provide a solution for traders so that they can maintain a systematic approach to *"reinforce"* their trading strategies.

`reinforce-trader` emphasizes the use of technical pattarns when traders make trading decisions. Traders often use technical patterns to find entry points and exit points. e.g Drawing lines of resistance levels and supporting levels, Drawing a triangle pattern, ...etc. Therefore, `reinforce-traders` allows you to upload an image to capture the moment of trade. I personally use [TradingView](https://www.tradingview.com/) to draw lines and you can easily download the chart image using Tradingview's "Take a Snapshot" function.


## How to start
**!! The "docker compose up -d --build" doesn't work now. All endpoints are not available (404 Not Found) if you use a container to run the server**
Remember to prepare a .env file (check the .env.sample) before starting the servers

### 1. Setup a MongoDB via docker
```bash
docker compose up -d --build mongodb
```
### 2. Start the reinforce-trader server

```python
# run_app.py
from dotenv import load_dotenv

load_dotenv('.env')

from reinforce_trader.main import create_app

app = create_app()
```
```bash
uvicorn run_app:app --port 8000
```
### 3. Start the dash app
```bash
python run_dash_app.py
```
