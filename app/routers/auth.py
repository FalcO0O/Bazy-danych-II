from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas import UserCreate, UserOut, Token, TokenRefreshRequest
from database import users_collection
from utils import get_password_hash, verify_password, create_access_token, create_refresh_token, log_action
from dependencies import get_current_user
from bson import ObjectId
from datetime import timedelta
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES

router = APIRouter(
    prefix="",
    tags=["auth"]
)


@router.post("/register", response_model=UserOut)
async def register(user: UserCreate):
    """
    Rejestracja nowego użytkownika.
    - sprawdzamy, czy e-mail nie jest zajęty,
    - haszujemy hasło,
    - zapisujemy do bazy,
    - zwracamy nowe dane (bez hasła).
    """
    # Sprawdź czy istnieje użytkownik o danym emailu
    if await users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Użytkownik o takim adresie email już istnieje")

    # Hashujemy hasło i tworzymy obiekt do zapisania
    hashed_pw = get_password_hash(user.password)
    user_dict = user.model_dump()
    user_dict["hashed_password"] = hashed_pw
    user_dict["role"] = "user"     # domyślna rola
    user_dict["refresh_tokens"] = []
    del user_dict["password"]

    # Zapis do bazy
    result = await users_collection.insert_one(user_dict)
    new_user = await users_collection.find_one({"_id": result.inserted_id})

    # Log akcji
    await log_action(str(new_user["_id"]), "register", "Rejestracja nowego użytkownika")

    return UserOut(
        id=str(new_user["_id"]),
        username=new_user["username"],
        email=new_user["email"],
        role=new_user["role"]
    )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Logowanie użytkownika. Używamy fieldów:
    - username (przechowujemy tam email),
    - password.
    Generujemy access i refresh token, zapisujemy refresh_token w bazie.
    """
    # Pobierz user po emailu
    user = await users_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Nieprawidłowy email lub hasło")

    # Stwórz tokeny
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "role": user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user["_id"]), "role": user["role"]},
        expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    )

    # Zapisz refresh_token w bazie
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$push": {"refresh_tokens": refresh_token}}
    )

    # Zaloguj akcję
    await log_action(str(user["_id"]), "login", "Użytkownik zalogowany")

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/token/refresh", response_model=Token)
async def refresh_access_token(body: TokenRefreshRequest):
    """
    Odświeżenie tokena: klient podaje refresh_token.
    Sprawdzamy, czy token jest ważny i czy znajduje się w liście refresh_tokens u użytkownika.
    """
    try:
        payload = jwt.decode(body.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Nieprawidłowy token odświeżania")
    except JWTError:
        raise HTTPException(status_code=401, detail="Nieprawidłowy token odświeżania")

    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user or body.refresh_token not in user.get("refresh_tokens", []):
        raise HTTPException(status_code=401, detail="Nieprawidłowy token odświeżania")

    # Tworzymy nowe tokeny
    new_access = create_access_token(
        data={"sub": str(user["_id"]), "role": user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    new_refresh = create_refresh_token(
        data={"sub": str(user["_id"]), "role": user["role"]},
        expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    )

    # Usuwamy stary refresh_token i dodajemy nowy
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$pull": {"refresh_tokens": body.refresh_token}}
    )
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$push": {"refresh_tokens": new_refresh}}
    )

    await log_action(str(user["_id"]), "refresh_token", "Odświeżono token")

    return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user), body: TokenRefreshRequest = None):
    """
    Wylogowanie: czyścimy refresh_tokeny u użytkownika.
    """
    await users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"refresh_tokens": []}}
    )
    await log_action(str(current_user["_id"]), "logout", "Wylogowano użytkownika")
    return {"message": "Wylogowano"}
