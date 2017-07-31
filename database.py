from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def configure_db(db_path):
    engine = create_engine(
        str(db_path),
        echo=False,
        encoding='utf-8')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

Base = declarative_base()


class City(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    link = Column(String(50))
    school = relationship('School', back_populates='city')

    def __repr__(self):
        return "<City(city_name='%s')>" % self.name


class School(Base):
    __tablename__ = 'schools'

    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('cities.id'))
    name = Column(String(500))
    type = Column(String(500))
    address = Column(String(500))
    phones = Column(String(500))
    website = Column(String(500))
    email = Column(String(500))
    link = Column(String(500))

    city = relationship("City", back_populates="school")
    faculty = relationship("Faculty", back_populates="school")

    def __repr__(self):
        return "<School(name='%s', link='%s')>" % (
            self.name, self.link)


class Faculty(Base):
    __tablename__ = 'faculties'

    id = Column(Integer, primary_key=True)
    school_id = Column(Integer, ForeignKey('schools.id'))
    study_type = Column(String(50))
    free_places = Column(Integer)
    available_places = Column(Integer)
    competition_link = Column(String(50))
    applied_number = Column(Integer)
    entered_number = Column(Integer)
    study_dates = Column(String(500))
    first_year_is = Column(String(500))
    recommended_number = Column(Integer)
    demanded_subjects = Column(String(1000))
    degree = Column(String(500))
    domain = Column(String(500))
    faculty = Column(String(500))
    specialization = Column(String(500))

    school = relationship("School", back_populates="faculty")
    student = relationship("Student", back_populates="faculty")

    def __repr__(self):
        return "<Faculty(uni_id='%s', link='%s')>" % (
            self.school_id, self.competition_link)


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    faculty_id = Column(Integer, ForeignKey('faculties.id'))
    name = Column(String(50))
    priority = Column(Integer)

    school_certificate = Column(Float)
    points = Column(Float)
    zno = Column(Float)

    entrance_points = Column(String(20))
    additional_points = Column(String(20))
    original_docs = Column(String(10))

    faculty = relationship("Faculty", back_populates="student")

    def __repr__(self):
        return "<Student(student_name='%s', student_points='%s', original_docs='%s')>" % (
            self.name, self.points, self.original_docs)
