"""
Database Configuration
Supports both SQLite (development) and PostgreSQL (production)
"""

import os
import logging
from urllib.parse import urlparse
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)

def get_database_config(database_url: str) -> dict:
    """
    Parse database URL and return SQLAlchemy configuration
    Supports both SQLite and PostgreSQL
    """
    config = {
        'SQLALCHEMY_DATABASE_URI': database_url,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_ENGINE_OPTIONS': {}
    }
    
    # Parse the database URL
    parsed = urlparse(database_url)
    
    if parsed.scheme in ('postgresql', 'postgres'):
        # PostgreSQL specific configuration
        config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': int(os.getenv('DATABASE_POOL_SIZE', '10')),
            'max_overflow': int(os.getenv('DATABASE_MAX_OVERFLOW', '20')),
            'pool_timeout': int(os.getenv('DATABASE_POOL_TIMEOUT', '30')),
            'pool_recycle': int(os.getenv('DATABASE_POOL_RECYCLE', '3600')),
            'pool_pre_ping': True,  # Verify connections before using
            'echo': os.getenv('DATABASE_ECHO', 'false').lower() == 'true',
            'connect_args': {
                'connect_timeout': 10,
                'application_name': 'lane_mcp'
            }
        }
        logger.info("Configured for PostgreSQL database")
        
    elif parsed.scheme == 'sqlite':
        # SQLite specific configuration
        config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_args': {
                'check_same_thread': False,
                'timeout': 30
            },
            'poolclass': pool.StaticPool if ':memory:' in database_url else pool.NullPool
        }
        logger.info("Configured for SQLite database")
        
    else:
        raise ValueError(f"Unsupported database scheme: {parsed.scheme}")
    
    return config


def init_database_engine(database_url: str):
    """
    Initialize database engine with appropriate configuration
    """
    parsed = urlparse(database_url)
    
    if parsed.scheme in ('postgresql', 'postgres'):
        # Ensure database exists
        try:
            # Connect to default postgres database first
            temp_url = database_url.replace(f'/{parsed.path[1:]}', '/postgres')
            temp_engine = create_engine(temp_url, isolation_level='AUTOCOMMIT')
            
            with temp_engine.connect() as conn:
                # Check if database exists
                result = conn.execute(
                    f"SELECT 1 FROM pg_database WHERE datname = '{parsed.path[1:]}'"
                )
                if not result.fetchone():
                    # Create database
                    conn.execute(f"CREATE DATABASE {parsed.path[1:]}")
                    logger.info(f"Created database: {parsed.path[1:]}")
                else:
                    logger.info(f"Database already exists: {parsed.path[1:]}")
                    
        except Exception as e:
            logger.warning(f"Could not check/create database: {e}")
    
    # Create the main engine
    config = get_database_config(database_url)
    engine = create_engine(
        config['SQLALCHEMY_DATABASE_URI'],
        **config['SQLALCHEMY_ENGINE_OPTIONS']
    )
    
    return engine


def test_database_connection(database_url: str) -> bool:
    """
    Test database connection
    """
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False