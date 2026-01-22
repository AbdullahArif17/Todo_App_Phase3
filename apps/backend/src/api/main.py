from fastapi import FastAPI
from .v1.auth import router as auth_router
from .v1.todos import router as todos_router

app = FastAPI(title="Todo Web Application API")

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(todos_router, prefix="/api/v1/todos", tags=["Todos"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo Web Application API"}