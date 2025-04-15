from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from api import admin_router, users_router, coworkings_router, booking_router
from pathlib import Path

app = FastAPI(title='chupapis')

BASE_DIR_APP = Path(__file__).resolve().parent

app.mount("/static", StaticFiles(directory=BASE_DIR_APP / "static"), name='static')

app.include_router(users_router)
app.include_router(booking_router)
app.include_router(admin_router)
app.include_router(coworkings_router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    try:
        error = str(exc.errors()[0].get('msg', 'An error occured'))
    except: error = 'An error occured'
    
    return JSONResponse(
        status_code=422,
        content={
            'status': 'error',
            'message': error
        },
    )

def custom_openapi():
    """422 error body replace"""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            responses = operation.get("responses")
            if responses and "422" in responses:
                responses.pop("422")
                responses["422"] = {
                    "description": "Unprocessable entity",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string"},
                                    "message": {"type": "string"},
                                },
                            }
                        }
                    },
                }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
