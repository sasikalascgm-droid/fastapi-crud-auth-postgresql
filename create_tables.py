from database import engine, Base
from models import Student, User

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")