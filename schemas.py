"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# Learning app specific schemas

class WorksheetSubmission(BaseModel):
    """
    Stores a student's LKPD (worksheet) submission
    Collection: "worksheetsubmission"
    """
    name: str = Field(..., description="Student full name")
    class_name: Optional[str] = Field(None, description="Class or group")
    answers: Dict[str, Any] = Field(..., description="Key-value answers for worksheet questions")

class Reflection(BaseModel):
    """
    Stores a student's reflection after completing LKPD
    Collection: "reflection"
    """
    submission_id: str = Field(..., description="Related worksheet submission ID")
    reflection_text: str = Field(..., description="What the student learned/reflected")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Self-assessed understanding 1-5")

class QuizAttempt(BaseModel):
    """
    Stores an auto-graded quiz attempt
    Collection: "quizattempt"
    """
    name: str = Field(..., description="Student name")
    score: int = Field(..., ge=0, description="Final score")
    total: int = Field(..., ge=1, description="Total possible points")
    answers: List[str] = Field(..., description="Submitted answers in order")

# Example schemas retained for reference (not used by the app directly)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = Field(None, ge=0, le=120)
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    category: str
    in_stock: bool = True
