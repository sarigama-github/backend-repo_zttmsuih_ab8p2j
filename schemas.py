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
from typing import Optional, List
from datetime import date

# Fitness app schemas

class Exercise(BaseModel):
    """
    Exercise library schema
    Collection name: "exercise"
    """
    name: str = Field(..., description="Exercise name, e.g., Bench Press")
    muscle_group: Optional[str] = Field(None, description="Primary muscle group")
    equipment: Optional[str] = Field(None, description="Equipment needed")
    notes: Optional[str] = Field(None, description="Form tips or notes")

class WorkoutItem(BaseModel):
    exercise_id: Optional[str] = Field(None, description="Linked exercise id (string)")
    exercise_name: str = Field(..., description="Exercise display name")
    sets: int = Field(..., ge=1, le=20, description="Number of sets")
    reps: int = Field(..., ge=1, le=100, description="Target reps per set")
    rest_seconds: Optional[int] = Field(90, ge=0, le=600, description="Rest time between sets")

class Workout(BaseModel):
    """
    Workout templates schema
    Collection name: "workout"
    """
    title: str = Field(..., description="Workout title, e.g., Push Day")
    description: Optional[str] = Field(None, description="Short description")
    items: List[WorkoutItem] = Field(default_factory=list, description="Ordered list of exercises in the workout")

class PerformedSet(BaseModel):
    set_number: int = Field(..., ge=1)
    weight: Optional[float] = Field(None, ge=0)
    reps: int = Field(..., ge=1)
    rpe: Optional[float] = Field(None, ge=1, le=10)

class SessionItem(BaseModel):
    exercise_name: str
    target_sets: int
    target_reps: int
    performed_sets: List[PerformedSet] = Field(default_factory=list)

class WorkoutSession(BaseModel):
    """
    Logged workout session
    Collection name: "workoutsession"
    """
    date_str: str = Field(..., description="ISO date string YYYY-MM-DD")
    workout_title: str
    notes: Optional[str] = None
    items: List[SessionItem] = Field(default_factory=list)

# Example schemas kept for reference (not used by app directly)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
