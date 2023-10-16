
def get_latest_trade(db, user_id, ticker, strategy):
    """
    Get the latest trade for a given ticker and strategy using MongoDB aggregation.

    :param db: pymongo.database.Database, the database containing the trades collection
    :param ticker: str, the ticker for which the trade should be retrieved
    :param strategy: str, the strategy for which the trade should be retrieved
    :return: dict, the latest trade or None if no trades are found
    """
    trades_collection = db['trades']
    pipeline = [
        {
            "$match": {
                "useId": user_id,
                "ticker": ticker,
                "strategy": strategy
            }
        },
        {
            "$sort": {"date": -1}  # sort by date descending
        },
        {
            "$limit": 1
        }
    ]

    trades = trades_collection.aggregate(pipeline)
    return trades[0] if trades else None  # Return None if no trades found


def get_current_position(db, user_id, ticker, strategy):
    """
    Get the current position for a given ticker and strategy using MongoDB aggregation.

    :param db: pymongo.database.Database, the database containing the trades collection
    :param ticker: str, the ticker for which the position should be retrieved
    :param strategy: str, the strategy for which the position should be retrieved
    :return: float, the current position
    """
    trades_collection = db['trades']
    pipeline = [
        {
            "$match": {
                "userId": user_id,
                "ticker": ticker,
                "strategy": strategy
            }
        },
        {
            "$group": {
                "_id": "$ticker",
                "position": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$side", 1]},  # Assuming 1 means "buy" or "long"
                            "$size",
                            {"$multiply": [-1, "$size"]}  # Assuming any other value means "sell" or "short"
                        ]
                    }
                }
            }
        }
    ]

    result = trades_collection.aggregate(pipeline)

    position = 0.0
    for res in result:
        position += res['position']
    
    return position  # Return 0 if no trades found

