import os

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware


from reinforce_trader.api.logger import get_logger
from reinforce_trader.api import config


error_logger = get_logger('error')
main_logger = get_logger('main')


def create_app():
    
    app = FastAPI()
    origins = [
        config.FRONTEND_URL,  # Allow your frontend origin
        # "https://yourfrontenddomain.com",  # You can also add production frontend origins
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # List of origins allowed (you can use ["*"] for all origins)
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods, or specify ["GET", "POST"]
        allow_headers=["*"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        body = await request.body()
        print(body)
        print(request.headers)
        error_logger.error(f'Validation Error: {request.method} | {request.url} | {exc.body}')
        return JSONResponse(
            status_code=422,
            content={"error": "Missing required field", "body": exc.body},
        )
    
    # catch all unexpected error
    @app.exception_handler(Exception)
    async def unexpected_exception_handler(request: Request, exc: Exception):
        # body = request.body()
        error_logger.error(f'Unexpected Error: {request.method} | {request.url} | {exc}')
        # Custom handling of the unexpected error
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "body": str(exc)},
        )
    
    # catch all known http exception
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        error_logger.error(f'Http Error: {request.method} | {request.url} | {exc.detail}')
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )

    # health checking
    @app.get('/health')
    async def health():
        return {
            "status": "ok"
        }
    
        # add routers
    from reinforce_trader.api.trades.router import trades_router
    from reinforce_trader.api.tickers.router import tickers_router
    from reinforce_trader.api.strategies.router import strategies_router
    from reinforce_trader.api.historical_data.router import historical_data_router
    
    app.include_router(trades_router)
    app.include_router(tickers_router)
    app.include_router(strategies_router)
    app.include_router(historical_data_router)

    allowed_host = os.getenv('ALLOWED_HOST', '*')
    # app.add_middleware(RouterLoggingMiddleware, logger=main_logger)
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=[allowed_host]
    )


    return app