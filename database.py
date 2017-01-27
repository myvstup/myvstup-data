from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class City(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True)
    city_name = Column(String)
    city_link = Column(String)

    def __repr__(self):
        return "<City(city_name='%s')" % self.city_name


class UniverInfo(Base):
    __tablename__ = 'uni_info'

    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('cities.id'))
    uni_name = Column(String)
    uni_type = Column(String)
    address = Column(String)
    phones = Column(String)
    website = Column(String)
    email = Column(String)
    link = Column(String)

    city = relationship("City", back_populates="uni_info")

    def __repr__(self):
        return "<Univer(uni_name='%s', address='%s')>" % (
            self.uni_name, self.address)


class UniverData(Base):
    __tablename__ = 'uni_speciality_data'

    id = Column(Integer, primary_key=True)
    uni_id = Column(Integer, ForeignKey('uni_info.id'))
    study_type = Column(String)
    free_places = Column(Integer)
    paid_places = Column(Integer)
    competition_link = Column(String)
    num_applied = Column(Integer)
    num_entered = Column(Integer)
    num_recommended = Column(Integer)
    required_subj = Column(JSON)
    degree = Column(String)
    degree_subname = Column(String)
    faculty = Column(String)
    specialization_1 = Column(String)
    specialization_2 = Column(String)

    university_data = relationship("UniverInfo", back_populates="uni_speciality_data")

    def __repr__(self):
        return "<UniverData(uni_id='%s', link='%s')>" % (
            self.uni_id, self.competition_link)


class Student(Base):
    __tablename__ = 'student_data'

    id = Column(Integer, primary_key=True)
    uni_data_id = Column(Integer, ForeignKey('uni_speciality_data.id'))
    student_name = Column(String)
    priority = Column(Integer)

    school_certificate = Column(Float)
    student_points = Column(Float)
    student_zno = Column(Float)

    entrance_points = Column(String)
    additional_points = Column(String)
    original_docs = Column(String)

    student = relationship("UniverData", back_populates="student_data")

    def __repr__(self):
        return "<Student(student_name='%s', student_points='%s', original_docs='%s')>" % (
            self.student_name, self.student_points, self.original_docs)