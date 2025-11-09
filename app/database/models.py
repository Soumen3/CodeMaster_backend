from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class OAuthProvider(str, enum.Enum):
    GOOGLE = "google"
    GITHUB = "github"


class Difficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class SubmissionStatus(str, enum.Enum):
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    RUNTIME_ERROR = "runtime_error"
    COMPILATION_ERROR = "compilation_error"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    provider = Column(Enum(OAuthProvider), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, provider={self.provider})>"


class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    difficulty = Column(Enum(Difficulty), nullable=False, index=True)
    
    # Code template fields for dynamic snippets
    function_name = Column(String(100), default="solution", nullable=True)
    parameters = Column(Text, nullable=True)  # JSON object: {"nums": "list[int]", "target": "int"}
    return_type = Column(String(50), nullable=True)  # e.g., "list", "int", "str"
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    test_cases = relationship("TestCase", back_populates="problem", cascade="all, delete-orphan")
    constraints = relationship("Constraint", back_populates="problem", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Problem(id={self.id}, title={self.title}, difficulty={self.difficulty})>"


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    problem_id = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True)
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)  # Optional explanation for the test case
    is_hidden = Column(Boolean, default=False, nullable=False)

    # Relationship to problem
    problem = relationship("Problem", back_populates="test_cases")

    def __repr__(self):
        return f"<TestCase(id={self.id}, problem_id={self.problem_id}, is_hidden={self.is_hidden})>"


class Constraint(Base):
    __tablename__ = "constraints"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    problem_id = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    order = Column(Integer, default=0, nullable=False)  # To maintain order of constraints
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship to problem
    problem = relationship("Problem", back_populates="constraints")

    def __repr__(self):
        return f"<Constraint(id={self.id}, problem_id={self.problem_id}, order={self.order})>"


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"


class ProblemTag(Base):
    __tablename__ = "problem_tags"

    problem_id = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)

    def __repr__(self):
        return f"<ProblemTag(problem_id={self.problem_id}, tag_id={self.tag_id})>"


class Solution(Base):
    __tablename__ = "solutions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)
    status = Column(Enum(SubmissionStatus), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User")
    problem = relationship("Problem")

    def __repr__(self):
        return f"<Solution(id={self.id}, user_id={self.user_id}, problem_id={self.problem_id}, status={self.status})>"
