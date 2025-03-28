"""
Models package initialization.

This module provides easy access to all models from a single import point.
"""
from app.models.user import User
from app.models.content import (
    Interest, Course, Lesson, 
    UserInterest, CourseInterest, UserCourse, UserLessonProgress
)
from app.models.forum import ForumTopic, ForumReply
from app.models.api_key import ApiKey