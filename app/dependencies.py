from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from schemas import TokenData
from config import SECRET_KEY, ALGORITHM
from database import users_collection
from bson import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Weryfikuje JWT (access token) i zwraca dokument użytkownika z bazy.
    Jeśli token jest nieprawidłowy lub użytkownik nie istnieje → 401.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nieprawidłowy token lub wygasł",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(id=user_id, role=role)
    except JWTError:
        raise credentials_exception

    user = await users_collection.find_one({"_id": ObjectId(token_data.id)})
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """
    (Dopisek) Możesz tu ewentualnie sprawdzić, czy konto użytkownika jest aktywne.
    Aktualnie po prostu zwraca użytkownika z get_current_user.
    """
    return current_user


async def get_current_admin(current_user: dict = Depends(get_current_user)):
    """
    Sprawdzenie, czy zalogowany użytkownik ma rolę 'admin'.
    Jeśli nie → 403 Forbidden.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Brak uprawnień administratora")
    return current_user
