from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    balance = Column(Float, default=0.0)
    referral_code = Column(String, unique=True)
    referred_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    referrals = relationship('User', backref='referrer', remote_side=[id])
    completed_tasks = relationship('TaskCompletion', back_populates='user')

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    reward = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    completions = relationship('TaskCompletion', back_populates='task')

class TaskCompletion(Base):
    __tablename__ = 'task_completions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    task_id = Column(Integer, ForeignKey('tasks.id'))
    completed_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default='pending')  # pending, approved, rejected
    
    # Relationships
    user = relationship('User', back_populates='completed_tasks')
    task = relationship('Task', back_populates='completions')

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # task_reward, referral_bonus, withdrawal
    status = Column(String, default='pending')  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User') 