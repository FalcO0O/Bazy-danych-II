from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importujemy routery
from routers import auth as auth_router
from routers import users as users_router
from routers import auctions as auctions_router

app = FastAPI(title="Aukcje Online API", version="1.0")

# Opcjonalnie: konfiguracja CORS (jeśli front np. na localhost:3000)
origins = [
    "http://localhost",
    "http://localhost:3000",
    # dodaj inne domeny, jeśli trzeba
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wpinamy routery do aplikacji
app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(auctions_router.router)

# Prosty root endpoint do sprawdzenia, czy API żyje
@app.get("/")
async def root():
    return {"message": "Aukcje Online API jest dostępne."}
