from fastapi import FastAPI
from routers import users, auth

app = FastAPI(
    title="Auction API",
    description="API for the auction application",
    version="1.0.0"
)

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Auction API!"}
