from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Prospect(Base):
    __tablename__ = "prospects"

    id = Column(Integer, primary_key=True, index=True)

    fullname = Column(String, nullable=False)
    linkedin_url = Column(String, unique=True)
    country = Column(String)
    job_title = Column(String)
    followers = Column(Integer)
    company = Column(String)

    score = Column(Integer, default=0)


    @property
    def name(self):
        return self.fullname


    @property
    def headline(self):
        return self.job_title


    score_details = relationship(
        "ScoreDetail",
        back_populates="prospect",
        cascade="all, delete-orphan"
    )


    qualification = relationship(
        "Qualification",
        back_populates="prospect",
        cascade="all, delete-orphan",
        uselist=False
    )

class ScoreDetail(Base):
    __tablename__ = "score_details"

    id = Column(Integer, primary_key=True)

    prospect_id = Column(
        Integer,
        ForeignKey("prospects.id")
    )

    criterion = Column(String)
    points = Column(Integer)
    comment = Column(String)

    prospect = relationship(
        "Prospect",
        back_populates="score_details"
    )


class Qualification(Base):

    __tablename__ = "qualifications"


    id = Column(
        Integer,
        primary_key=True
    )


    prospect_id = Column(
        Integer,
        ForeignKey("prospects.id"),
        nullable=False
    )


    profession = Column(
        String
    )


    sector = Column(
        String
    )


    target_market = Column(
        String
    )


    icp_match = Column(
        Integer
    )


    confidence = Column(
        Integer
    )


    decision_status = Column(
        String
    )


    decision_priority = Column(
        String
    )


    reason = Column(
        String
    )


    evidence = Column(
        String
    )


    prospect = relationship(
        "Prospect",
        back_populates="qualification"
    )

    offer_detected = Column(
    Integer
    )


    authority_signals = Column(
    String
    )


    content_signals = Column(
    String
    )


    commercial_signals = Column(
    String
    )

    exclusion_reason = Column(
    String
    )