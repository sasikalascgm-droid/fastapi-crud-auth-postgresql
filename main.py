from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Student, User
from schemas import StudentCreate, StudentUpdate, UserCreate

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)


app = FastAPI()


# =========================
# JWT SECURITY
# =========================

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    username = verify_token(token)

    return username


# =========================
# DATABASE CONNECTION
# =========================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================
# HOME
# =========================

@app.get("/")
def index():
    return {
        "message": "Student CRUD API"
    }


# =========================
# CREATE STUDENT
# =========================

@app.post("/create_student")
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    new_student = Student(
        name=student.name,
        age=student.age,
        year=student.year
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return new_student


# =========================
# GET STUDENT BY ID
# =========================

@app.get("/get-student/{student_id}")
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student


# =========================
# GET ALL STUDENTS
# =========================

@app.get("/students")
def get_students(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    students = db.query(Student).all()

    return students


# =========================
# UPDATE STUDENT
# =========================

@app.put("/update_student/{student_id}")
def update_student(
    student_id: int,
    student: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    existing_student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if existing_student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    if student.name is not None:
        existing_student.name = student.name

    if student.age is not None:
        existing_student.age = student.age

    if student.year is not None:
        existing_student.year = student.year

    db.commit()
    db.refresh(existing_student)

    return existing_student


# =========================
# DELETE STUDENT
# =========================

@app.delete("/delete_student/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    db.delete(student)
    db.commit()

    return {
        "message": "Student deleted successfully"
    }


# =========================
# USER REGISTER
# =========================

@app.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        username=user.username,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "username": new_user.username
    }


# =========================
# USER LOGIN
# =========================

@app.post("/login")
def login(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(
        user.password,
        existing_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token(
        existing_user.username
    )

    return {
        "message": "Login successful",
        "username": existing_user.username,
        "access_token": token,
        "token_type": "bearer"
    }