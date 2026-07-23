from app.collector import fetch_trades
from config import BASE_URL


def main():

    trades = fetch_trades(BASE_URL)

    print(type(trades))
    print(len(trades))


if __name__ == "__main__":
    main()