import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base
import asyncio

# Database configuration
DATABASE_URL = "sqlite+aiosqlite:///referral_bot.db"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create async session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    """Initialize the database and create tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    """Get a database session"""
    async with async_session() as session:
        yield session

async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int):
    """Get user by telegram ID"""
    from models import User
    result = await session.execute(
        User.__table__.select().where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()

async def create_user(session: AsyncSession, telegram_id: int, username: str, 
                     first_name: str, last_name: str, referral_code: str):
    """Create a new user"""
    from models import User
    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        referral_code=referral_code
    )
    session.add(user)
    await session.commit()
    return user

async def get_task_by_id(session: AsyncSession, task_id: int):
    """Get task by ID"""
    from models import Task
    result = await session.execute(
        Task.__table__.select().where(Task.id == task_id)
    )
    return result.scalar_one_or_none()

async def create_task_completion(session: AsyncSession, user_id: int, task_id: int):
    """Create a new task completion record"""
    from models import TaskCompletion
    completion = TaskCompletion(
        user_id=user_id,
        task_id=task_id
    )
    session.add(completion)
    await session.commit()
    return completion

async def create_transaction(session: AsyncSession, user_id: int, amount: float, 
                           transaction_type: str):
    """Create a new transaction"""
    from models import Transaction
    transaction = Transaction(
        user_id=user_id,
        amount=amount,
        type=transaction_type
    )
    session.add(transaction)
    await session.commit()
    return transaction 