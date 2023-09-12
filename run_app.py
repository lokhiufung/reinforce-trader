from dotenv import load_dotenv

load_dotenv('.env')

from reinforce_trader.main import create_app


app = create_app()