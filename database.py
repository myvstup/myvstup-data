from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class City(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    link = Column(String(50))
    university = relationship('University', back_populates='city')

    def __repr__(self):
        return "<City(city_name='%s')>" % self.name


class University(Base):
    __tablename__ = 'universities'

    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('cities.id'))
    name = Column(String(500))
    type = Column(String(500))
    address = Column(String(500))
    phones = Column(String(50))
    website = Column(String(50))
    email = Column(String(50))
    link = Column(String(500))

    city = relationship("City", back_populates="university")
    faculty = relationship("Faculty", back_populates="university")

    def __repr__(self):
        return "<University(uni_name='%s', link='%s')>" % (
            self.name, self.link)


class Faculty(Base):
    __tablename__ = 'faculties'

    id = Column(Integer, primary_key=True)
    uni_id = Column(Integer, ForeignKey('universities.id'))
    study_type = Column(String(50))
    free_places = Column(Integer)
    paid_places = Column(Integer)
    competition_link = Column(String(50))
    num_applied = Column(Integer)
    num_entered = Column(Integer)
    num_recommended = Column(Integer)
    required_subj = Column(String(500))
    degree = Column(String(500))
    degree_subname = Column(String(500))
    faculty = Column(String(500))
    specialization_1 = Column(String(500))
    specialization_2 = Column(String(500))

    university = relationship("University", back_populates="faculty")
    student = relationship("Student",
                           back_populates="applied_to")

    def __repr__(self):
        return "<Faculty(uni_id='%s', link='%s')>" % (
            self.uni_id, self.competition_link)


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    uni_data_id = Column(Integer, ForeignKey('faculties.id'))
    name = Column(String(50))
    priority = Column(Integer)

    school_certificate = Column(Float)
    points = Column(Float)
    zno = Column(Float)

    entrance_points = Column(String(20))
    additional_points = Column(String(20))
    original_docs = Column(String(10))

    applied_to = relationship("Faculty", back_populates="student")

    def __repr__(self):
        return "<Student(student_name='%s', student_points='%s', original_docs='%s')>" % (
            self.name, self.points, self.original_docs)
