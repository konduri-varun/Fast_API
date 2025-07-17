from datetime import datetime, timedelta
from typing import Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient

# --- App & DB Setup ---
app = FastAPI()
client = MongoClient("mongodb://localhost:27017")
db = client["college_db"]
user_col = db["users"]
student_col = db["students"]

# --- JWT Config ---
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Password Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- OAuth2 Token Scheme ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# --- Pydantic Models ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Student(BaseModel):
    roll_no: str
    name: str
    branch: str
    marks: Dict[str, int]

# --- Utils ---
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_pwd, hashed_pwd):
    return pwd_context.verify(plain_pwd, hashed_pwd)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = user_col.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/")
def root():
    return {"message": "Welcome to the Student Management API"}

# --- Auth Routes ---
@app.post("/register", response_model=Dict)
def register(user: UserCreate):
    if user_col.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_pwd = hash_password(user.password)
    user_col.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hashed_pwd
    })
    return {"message": "User registered successfully"}

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_col.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token(data={"sub": user["username"]}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}

# --- Student CRUD Routes (Protected) ---
@app.post("/students")
def create_student(student: Student, user=Depends(get_current_user)):
    if student_col.find_one({"roll_no": student.roll_no}):
        raise HTTPException(status_code=400, detail="Roll number already exists")
    student_col.insert_one(student.dict())
    return student

@app.get("/students")
def get_students(user=Depends(get_current_user)):
    return list(student_col.find({}, {"_id": 0}))

@app.get("/students/{roll_no}")
def get_student(roll_no: str, user=Depends(get_current_user)):
    student = student_col.find_one({"roll_no": roll_no})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student.pop("_id", None)
    return student

@app.put("/students/{roll_no}")
def update_student(roll_no: str, update_data: Dict, user=Depends(get_current_user)):
    result = student_col.update_one({"roll_no": roll_no}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    student = student_col.find_one({"roll_no": roll_no})
    student.pop("_id", None)
    return student

@app.delete("/students/{roll_no}")
def delete_student(roll_no: str, user=Depends(get_current_user)):
    result = student_col.delete_one({"roll_no": roll_no})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student record deleted"}
