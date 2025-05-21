import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from pydantic import BaseModel
from models import User
from database import get_db


load_dotenv()


router = APIRouter()


class UserCreate(BaseModel):
    name: str
    email: str


class UserUpdate(BaseModel):
    name: str
    email: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str


class QueryRequest(BaseModel):
    query: str


@router.post("/swagger", response_model=List[Dict[str, Any]])
def execute_query(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        result = db.execute(text(request.query))
        db.commit()

        # Если это обычный запрос с возвратом строк
        if result.returns_rows:
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            return rows

        # Если это вызов функции, возвращающей одну запись
        scalar_result = result.scalar()
        if scalar_result is not None:
            return [{"result": scalar_result}]

        return []

    except Exception as e:
        print(f"Error executing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = User(email=user.email, name=user.name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    try:
        return db.query(User).all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/users/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/users/{id}", response_model=UserUpdate)
def update_user(id: int, user: UserUpdate, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.id == id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        if db_user.id == 1 or db_user.id == 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden"
            )

        db_user.name = user.name
        db_user.email = user.email
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/users/{id}")
def delete_user(id: int, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.id == id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        if db_user.id == 1 or db_user.id == 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden"
            )

        db.delete(db_user)
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

