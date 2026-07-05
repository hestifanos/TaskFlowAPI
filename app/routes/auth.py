"""Registration and login endpoints."""
import sqlite3

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.database import get_conn
from app.security import create_token, hash_password, verify_password

router = APIRouter()


class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


@router.post("/register", status_code=201)
def register(body: Credentials):
    try:
        with get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (body.email.lower(), hash_password(body.password)),
            )
            user_id = cur.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Email already registered")
    return {"token": create_token(user_id, body.email)}


@router.post("/login")
def login(body: Credentials):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, password_hash FROM users WHERE email = ?", (body.email.lower(),)
        ).fetchone()
    if row is None or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"token": create_token(row["id"], body.email)}
