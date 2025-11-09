from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional, List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy import Column, Integer, String, Enum as SAEnum, ForeignKey, create_engine, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
import os

# -------------------- Configuration --------------------
DATABASE_URL = "sqlite:///./app.db"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day for convenience
SECRET_KEY = "change-this-secret-key-to-a-secure-random-value"
ALGORITHM = "HS256"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -------------------- App & DB setup --------------------
app = FastAPI(title="FastAPI SQLite Example")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# -------------------- Models --------------------
class UserType(str, Enum):
    CREATOR = "CREATOR"
    COMPANY = "COMPANY"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    type = Column(SAEnum(UserType), nullable=False)

    products = relationship("Product", back_populates="owner")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="products")
    advertisements = relationship("Advertisement", back_populates="product", cascade="all, delete")

class Advertisement(Base):
    __tablename__ = "advertisements"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)

    product = relationship("Product", back_populates="advertisements")

Base.metadata.create_all(bind=engine)

# -------------------- Pydantic Schemas --------------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    type: UserType

class UserOut(BaseModel):
    id: int
    email: EmailStr
    type: UserType

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int

    class Config:
        orm_mode = True

class AdvertisementCreate(BaseModel):
    product_id: int
    description: Optional[str] = None

class AdvertisementOut(BaseModel):
    id: int
    product_id: int
    description: Optional[str]
    file_path: Optional[str]

    class Config:
        orm_mode = True

# -------------------- Utility functions --------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, stored_password: str) -> bool:
    # Direct string comparison (no hashing)
    return plain_password == stored_password

def get_password_hash(password: str) -> str:
    # Return password as-is (no hashing)
    return password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# -------------------- Auth helpers --------------------
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

# -------------------- Routes: Authentication --------------------
@app.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        type=user_in.type,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# -------------------- Routes: Products --------------------
@app.post("/products", response_model=ProductOut)
def create_product(product_in: ProductCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = Product(name=product_in.name, description=product_in.description, owner_id=current_user.id)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@app.get("/products", response_model=List[ProductOut])
def list_products(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@app.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/products/owner/{owner_id}", response_model=List[ProductOut])
def get_products_by_owner(owner_id: int, db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.owner_id == owner_id).all()
    return products

@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db.delete(product)
    db.commit()
    return

# -------------------- Routes: Advertisements --------------------
@app.post("/advertisements", response_model=AdvertisementOut)
async def create_advertisement(
    product_id: int,
    description: Optional[str] = None,
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions to add advertisement for this product")

    file_path = None
    if file:
        filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        destination = os.path.join(UPLOAD_DIR, filename)
        with open(destination, "wb") as buffer:
            buffer.write(await file.read())
        file_path = destination

    ad = Advertisement(product_id=product_id, description=description, file_path=file_path)
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return ad

@app.get("/products/{product_id}/advertisements", response_model=List[AdvertisementOut])
def get_advertisements_by_product(product_id: int, db: Session = Depends(get_db)):
    advertisements = db.query(Advertisement).filter(Advertisement.product_id == product_id).all()
    return advertisements

@app.get("/advertisements", response_model=List[AdvertisementOut])
def list_ads(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    ads = db.query(Advertisement).offset(skip).limit(limit).all()
    return ads

@app.get("/advertisements/{ad_id}", response_model=AdvertisementOut)
def get_ad(ad_id: int, db: Session = Depends(get_db)):
    ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad

@app.delete("/advertisements/{ad_id}", status_code=204)
def delete_ad(ad_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    # ensure only owner of product can delete
    if ad.product.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    # delete file if exists
    if ad.file_path and os.path.exists(ad.file_path):
        try:
            os.remove(ad.file_path)
        except Exception:
            pass
    db.delete(ad)
    db.commit()
    return

# -------------------- Simple startup route --------------------
@app.get("/")
def read_root():
    return {"message": "FastAPI app with SQLite (users, products, advertisements). Enum: CREATOR/COMPANY"}
