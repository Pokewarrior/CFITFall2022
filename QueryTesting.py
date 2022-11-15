from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db = declarative_base()

USERNAME="access"
PASSWORD=""
PROJECT_ID ="Cfit"
INSTANCE_NAME ="cfitdata"
DB_IP="34.145.150.163"
DB_NAME="CFITD"

db_connection = f"mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{DB_IP}/{DB_NAME}"
class assessments(db):
    __tablename__ = 'assessments'   
    id = Column(Integer, primary_key = True)
    session_id = Column(Integer)
    student_id = Column(Integer)
    student_name = Column(String(256))
    course = Column(String(256))
    course_instructor = Column(String(256))
    semester = Column(String(256))
    client = Column(String(256))
    disorder = Column(String(256))
    instructor_id = Column(Integer)
    client_id = Column(Integer)
    date = Column(DateTime)
   

