import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar

def format_currency(amount):
    """Format amount as currency string"""
    return f"${amount:.2f}"

def get_date_range_options():
    """Get predefined date range options"""
    today = datetime.now().date()
    return {
        "Today": (today, today),
        "This Week": (today - timedelta(days=today.weekday()), today),
        "This Month": (today.replace(day=1), today),
        "Last Month": get_last_month_range(),
        "Last 30 Days": (today - timedelta(days=30), today),
        "Last 90 Days": (today - timedelta(days=90), today),
        "This Year": (today.replace(month=1, day=1), today)
    }

def get_last_month_range():
    """Get the date range for last month"""
    today = datetime.now().date()
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    first_day_last_month = last_day_last_month.replace(day=1)
    return (first_day_last_month, last_day_last_month)

def calculate_budget_status(spent_amount, budget_amount):
    """Calculate budget status and return status info"""
    if budget_amount <= 0:
        return {
            "percentage": 0,
            "remaining": 0,
            "status": "No Budget Set",
            "color": "gray"
        }
    
    percentage = (spent_amount / budget_amount) * 100
    remaining = budget_amount - spent_amount
    
    if percentage >= 100:
        status = "Over Budget"
        color = "red"
    elif percentage >= 90:
        status = "Near Limit"
        color = "orange"
    elif percentage >= 75:
        status = "On Track"
        color = "yellow"
    else:
        status = "Good"
        color = "green"
    
    return {
        "percentage": min(percentage, 100),
        "remaining": remaining,
        "status": status,
        "color": color
    }

def get_spending_insights(expenses_df):
    """Generate spending insights from expense data"""
    if expenses_df.empty:
        return {}
    
    insights = {}
    
    # Convert date column to datetime
    expenses_df['date'] = pd.to_datetime(expenses_df['date'])
    
    # Most expensive category
    category_totals = expenses_df.groupby('category')['amount'].sum()
    insights['highest_category'] = {
        'category': category_totals.idxmax(),
        'amount': category_totals.max()
    }
    
    # Average daily spending
    date_range = (expenses_df['date'].max() - expenses_df['date'].min()).days
    if date_range > 0:
        insights['daily_average'] = expenses_df['amount'].sum() / date_range
    else:
        insights['daily_average'] = expenses_df['amount'].sum()
    
    # Most frequent category
    category_counts = expenses_df.groupby('category').size()
    insights['most_frequent_category'] = {
        'category': category_counts.idxmax(),
        'count': category_counts.max()
    }
    
    # Largest single expense
    max_expense = expenses_df.loc[expenses_df['amount'].idxmax()]
    insights['largest_expense'] = {
        'description': max_expense['description'],
        'amount': max_expense['amount'],
        'date': max_expense['date']
    }
    
    # Spending trend (comparing last 30 days to previous 30 days)
    current_date = datetime.now()
    last_30_days = expenses_df[
        expenses_df['date'] >= current_date - timedelta(days=30)
    ]['amount'].sum()
    
    previous_30_days = expenses_df[
        (expenses_df['date'] >= current_date - timedelta(days=60)) &
        (expenses_df['date'] < current_date - timedelta(days=30))
    ]['amount'].sum()
    
    if previous_30_days > 0:
        trend_percentage = ((last_30_days - previous_30_days) / previous_30_days) * 100
        insights['spending_trend'] = {
            'current_period': last_30_days,
            'previous_period': previous_30_days,
            'change_percentage': trend_percentage,
            'trend': 'increasing' if trend_percentage > 0 else 'decreasing'
        }
    
    return insights

def validate_expense_data(description, amount, category, date):
    """Validate expense input data"""
    errors = []
    
    if not description or description.strip() == "":
        errors.append("Description is required")
    
    if amount is None or amount <= 0:
        errors.append("Amount must be greater than 0")
    
    if not category or category.strip() == "":
        errors.append("Category is required")
    
    if not date:
        errors.append("Date is required")
    
    # Validate date format and reasonable range
    try:
        if isinstance(date, str):
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            parsed_date = datetime.combine(date, datetime.min.time())
        
        # Check if date is not in the future beyond today
        if parsed_date.date() > datetime.now().date():
            errors.append("Date cannot be in the future")
        
        # Check if date is not too far in the past (e.g., more than 10 years)
        if parsed_date.date() < datetime.now().date() - timedelta(days=3650):
            errors.append("Date seems too far in the past")
            
    except (ValueError, TypeError):
        errors.append("Invalid date format")
    
    return errors

def export_to_csv(data, filename=None):
    """Export DataFrame to CSV format"""
    if filename is None:
        filename = f"expenses_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return data.to_csv(index=False)

def export_to_json(data, filename=None):
    """Export DataFrame to JSON format"""
    if filename is None:
        filename = f"expenses_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    return data.to_json(orient='records', indent=2, date_format='iso')

def calculate_financial_metrics(expenses_df, budgets_df):
    """Calculate various financial metrics"""
    if expenses_df.empty:
        return {}
    
    expenses_df['date'] = pd.to_datetime(expenses_df['date'])
    current_month = datetime.now().strftime("%Y-%m")
    
    # Current month expenses
    current_month_expenses = expenses_df[
        expenses_df['date'].dt.strftime("%Y-%m") == current_month
    ]
    
    metrics = {
        'total_spent_current_month': current_month_expenses['amount'].sum(),
        'total_transactions_current_month': len(current_month_expenses),
        'average_transaction_current_month': current_month_expenses['amount'].mean() if not current_month_expenses.empty else 0,
        'total_budget': budgets_df['amount'].sum() if not budgets_df.empty else 0,
    }
    
    # Calculate remaining budget
    metrics['remaining_budget'] = metrics['total_budget'] - metrics['total_spent_current_month']
    
    # Calculate budget utilization percentage
    if metrics['total_budget'] > 0:
        metrics['budget_utilization'] = (metrics['total_spent_current_month'] / metrics['total_budget']) * 100
    else:
        metrics['budget_utilization'] = 0
    
    return metrics

def get_expense_statistics(expenses_df, category=None, date_range=None):
    """Get detailed statistics for expenses"""
    if expenses_df.empty:
        return {}
    
    # Filter by category if specified
    if category and category != "All":
        expenses_df = expenses_df[expenses_df['category'] == category]
    
    # Filter by date range if specified
    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        expenses_df['date'] = pd.to_datetime(expenses_df['date'])
        expenses_df = expenses_df[
            (expenses_df['date'] >= pd.Timestamp(start_date)) & 
            (expenses_df['date'] <= pd.Timestamp(end_date))
        ]
    
    if expenses_df.empty:
        return {}
    
    stats = {
        'count': len(expenses_df),
        'total': expenses_df['amount'].sum(),
        'mean': expenses_df['amount'].mean(),
        'median': expenses_df['amount'].median(),
        'std': expenses_df['amount'].std(),
        'min': expenses_df['amount'].min(),
        'max': expenses_df['amount'].max(),
        'q25': expenses_df['amount'].quantile(0.25),
        'q75': expenses_df['amount'].quantile(0.75)
    }
    
    return stats

def format_number_with_suffix(num):
    """Format large numbers with K, M suffixes"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return f"{num:.0f}"
