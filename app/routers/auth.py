from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.user import SignupRequest
from app.security import hash_password
from app.security import verify_password
from app.schemas.user import LoginRequest
from app.security import create_access_token
from app.dependencies.auth import get_current_user
from app.dependencies.auth import get_current_tenant
router = APIRouter()
@router.post("/signup")
def signup(
    request:SignupRequest,
    db:Session=Depends(get_db)
):
  tenant=Tenant(
    name=request.tenant_name
  )
  db.add(tenant)
  db.commit()
  db.refresh(tenant)
  user=User(
    email=request.email,
    hashed_password=hash_password(
        request.password
    ),
    tenant_id=tenant.id
  )
  db.add(user)
  db.commit()
  return "Sign up successfull"


@router.post("/login")
def login(user: LoginRequest, db: Session = Depends(get_db)):

    # 1. find user
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. verify password
    if not verify_password(
    user.password,
    db_user.hashed_password
):
        raise HTTPException(status_code=401, detail="Invalid password")

    # 3. create JWT
    token = create_access_token({
        "user_id": db_user.id,
        "tenant_id": db_user.tenant_id
    })

    # 4. return token
    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me")
def get_me(
    current_user:User=Depends(get_current_user)
):
  return {
        "id": current_user.id,
        "email": current_user.email,
        "tenant_id": current_user.tenant_id
    }

@router.get("/tenant")
def get_tenant(
    tenant_id=Depends(get_current_tenant)
):
    return {
        "tenant_id": tenant_id
    }