from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importujemy routery
from routers import auth as auth_router
from routers import users as users_router
from routers import auctions as auctions_router
from routers import reports as reports_router

app = FastAPI(title="Aukcje Online API", version="1.0")

# konfiguracja CORS (front na localhost:5173)
origins = [
    "http://localhost",
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wpinamy routery
app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(auctions_router.router)
app.include_router(reports_router.router)

@app.get("/")
async def root():
    '''Prosty root endpoint do sprawdzenia czy API żyje'''
    return {"message": "Aukcje Online API jest dostępne."}
