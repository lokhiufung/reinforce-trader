from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from reinforce_trader.api.logger import get_logger


error_logger = get_logger('error')
main_logger = get_logger('main')


def create_app():
    
    app = FastAPI()
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
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
            status_code=500,
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
    
    app.include_router(trades_router)
    app.include_router(tickers_router)
    app.include_router(strategies_router)

    # app.add_middleware(RouterLoggingMiddleware, logger=main_logger)

    return app