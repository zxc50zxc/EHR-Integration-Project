from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)
    role: str = "patient"
    date_of_birth: str | None = None
    gender: str | None = None
    phone: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    role: str
    patient_id: int | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user_id: int
    patient_id: int | None = None
    username: str
    role: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
