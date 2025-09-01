import sqlite3
import pandas as pd
from datetime import datetime
import os

DATABASE_NAME = "expenses.db"

def get_connection():
    """Get database connection"""
    return sqlite3.connect(DATABASE_NAME)

def init_db():
    """Initialize the database with required tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create budgets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT UNIQUE NOT NULL,
            amount REAL NOT NULL,
            period TEXT NOT NULL DEFAULT 'Monthly',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def add_expense(description, amount, category, date, notes=None):
    """Add a new expense to the database"""
    if not description or amount <= 0 or not category or not date:
        raise ValueError("All required fields must be provided and amount must be positive")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO expenses (description, amount, category, date, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (description, float(amount), category, date, notes))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_expenses():
    """Get all expenses from database"""
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM expenses ORDER BY date DESC, created_at DESC", conn)
        return df
    except Exception as e:
        return pd.DataFrame()
    finally:
        conn.close()

def update_expense(expense_id, description, amount, category, date, notes=None):
    """Update an existing expense"""
    if not description or amount <= 0 or not category or not date:
        raise ValueError("All required fields must be provided and amount must be positive")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE expenses 
            SET description=?, amount=?, category=?, date=?, notes=?
            WHERE id=?
        """, (description, float(amount), category, date, notes, expense_id))
        
        if cursor.rowcount == 0:
            raise ValueError("Expense not found")
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_expense(expense_id):
    """Delete an expense"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        
        if cursor.rowcount == 0:
            raise ValueError("Expense not found")
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_categories():
    """Get all unique categories from expenses"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT DISTINCT category FROM expenses ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        
        # Add some default categories if none exist
        if not categories:
            default_categories = [
                "Food & Dining", "Transportation", "Shopping", "Entertainment",
                "Bills & Utilities", "Healthcare", "Travel", "Education", "Other"
            ]
            return default_categories
        
        return categories
    except Exception as e:
        return ["Food & Dining", "Transportation", "Shopping", "Entertainment",
                "Bills & Utilities", "Healthcare", "Travel", "Education", "Other"]
    finally:
        conn.close()

def set_budget(category, amount, period="Monthly", description=None):
    """Set or update budget for a category"""
    if not category or amount <= 0:
        raise ValueError("Category and positive amount are required")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Use INSERT OR REPLACE to handle both new budgets and updates
        cursor.execute("""
            INSERT OR REPLACE INTO budgets (category, amount, period, description, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (category, float(amount), period, description))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_budgets():
    """Get all budgets from database"""
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM budgets ORDER BY category", conn)
        return df
    except Exception as e:
        return pd.DataFrame()
    finally:
        conn.close()

def delete_budget(budget_id):
    """Delete a budget"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM budgets WHERE id=?", (budget_id,))
        
        if cursor.rowcount == 0:
            raise ValueError("Budget not found")
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_expense_summary(start_date=None, end_date=None):
    """Get expense summary with optional date filtering"""
    conn = get_connection()
    
    query = """
        SELECT 
            category,
            COUNT(*) as transaction_count,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount,
            MIN(amount) as min_amount,
            MAX(amount) as max_amount
        FROM expenses
    """
    params = []
    
    if start_date and end_date:
        query += " WHERE date BETWEEN ? AND ?"
        params = [start_date, end_date]
    elif start_date:
        query += " WHERE date >= ?"
        params = [start_date]
    elif end_date:
        query += " WHERE date <= ?"
        params = [end_date]
    
    query += " GROUP BY category ORDER BY total_amount DESC"
    
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        return pd.DataFrame()
    finally:
        conn.close()

def get_monthly_spending():
    """Get monthly spending totals"""
    conn = get_connection()
    
    query = """
        SELECT 
            strftime('%Y-%m', date) as month,
            SUM(amount) as total_amount,
            COUNT(*) as transaction_count
        FROM expenses 
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month DESC
    """
    
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        return pd.DataFrame()
    finally:
        conn.close()

def search_expenses(search_term):
    """Search expenses by description or notes"""
    if not search_term:
        return get_expenses()
    
    conn = get_connection()
    
    query = """
        SELECT * FROM expenses 
        WHERE description LIKE ? OR notes LIKE ? OR category LIKE ?
        ORDER BY date DESC, created_at DESC
    """
    search_pattern = f"%{search_term}%"
    
    try:
        df = pd.read_sql_query(query, conn, params=[search_pattern, search_pattern, search_pattern])
        return df
    except Exception as e:
        return pd.DataFrame()
    finally:
        conn.close()
