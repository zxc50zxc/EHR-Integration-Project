from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from backend.config import settings
from backend.database.models import Patient, User, UserRole
from backend.security.audit import log_audit
from backend.security.auth import create_access_token, create_refresh_token, hash_password, verify_password


class AuthService:
    @staticmethod
    def register_user(
        db: Session,
        username: str,
        email: str,
        full_name: str,
        password: str,
        role: str = "patient",
        date_of_birth: str | None = None,
        gender: str | None = None,
        phone: str | None = None,
    ) -> User:
        existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered",
            )

        if len(password) < 6:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 6 characters")

        try:
            user_role = UserRole(role)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role") from exc

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            password_hash=hash_password(password),
            role=user_role,
        )
        db.add(user)
        db.flush()

        if user_role == UserRole.patient:
            names = full_name.split()
            first_name = names[0] if names else username
            last_name = " ".join(names[1:]) if len(names) > 1 else "Patient"
            patient = Patient(
                mrn=f"USR{user.id:06d}",
                first_name=first_name,
                last_name=last_name,
                date_of_birth=date_of_birth or "1900-01-01",
                gender=gender or "unknown",
                phone=phone,
                email=email,
            )
            db.add(patient)
            db.flush()
            user.patient_id = patient.id

        db.commit()
        db.refresh(user)

        log_audit(user.id, "register", "User", user.id, db=db)
        db.commit()
        return user

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str, ip_address: str | None = None) -> dict:
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.password_hash):
            log_audit(None, "failed_login", "User", None, f"Username: {username}", ip_address, db=db)
            db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account is inactive")

        log_audit(user.id, "login", "User", user.id, ip_address=ip_address, db=db)
        db.commit()

        return {
            "access_token": create_access_token(data={"sub": str(user.id)}),
            "refresh_token": create_refresh_token(data={"sub": str(user.id)}),
            "token_type": "bearer",
            "user_id": user.id,
            "patient_id": user.patient_id,
            "username": user.username,
            "role": UserRole(user.role).value,
        }

    @staticmethod
    def refresh_access_token(refresh_token: str) -> dict[str, str]:
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            token_type = payload.get("type")

            if user_id is None or token_type != "refresh":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

            access_token = create_access_token(data={"sub": str(user_id)})
            return {"access_token": access_token, "token_type": "bearer"}
        except JWTError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    @staticmethod
    def logout(user: User, request: Request | None = None, db: Session | None = None) -> dict[str, str]:
        log_audit(
            user.id,
            "logout",
            "User",
            user.id,
            ip_address=request.client.host if request and request.client else None,
            db=db,
        )
        if db:
            db.commit()
        return {"message": "Logged out successfully"}
