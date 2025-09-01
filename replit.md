# Expense Tracker

## Overview

This is a personal finance management application built with Streamlit that allows users to track expenses, manage budgets, and analyze spending patterns. The application provides a web-based interface for recording financial transactions, setting category-based budgets, and visualizing spending data through interactive charts and dashboards.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web framework for rapid development of data applications
- **Layout**: Wide layout with expandable sidebar for navigation
- **Visualization**: Plotly Express and Plotly Graph Objects for interactive charts, Matplotlib for static plots
- **Navigation**: Multi-page application with sidebar-based page selection
- **Pages**: Dashboard, Add Expense, Manage Expenses, Budget Management, Analytics, Export Data

### Backend Architecture
- **Database Layer**: SQLite database with dedicated database module for data persistence
- **Data Models**: Two main entities - expenses and budgets
- **Business Logic**: Utility functions for currency formatting, date range calculations, and budget status analysis
- **Session Management**: Streamlit session state for managing application state and refresh triggers

### Data Storage
- **Database**: SQLite local database (`expenses.db`)
- **Expenses Table**: Stores transaction records with description, amount, category, date, notes, and timestamps
- **Budgets Table**: Stores budget limits per category with period-based budgeting (monthly default)
- **Data Processing**: Pandas DataFrames for data manipulation and analysis

### Key Design Patterns
- **Modular Architecture**: Separation of concerns with dedicated modules for database operations, utilities, and main application logic
- **Configuration Management**: Centralized page configuration with custom styling and layout settings
- **Error Handling**: Input validation for expense entries with proper error messaging
- **State Management**: Session-based state tracking for UI refresh and data consistency

## External Dependencies

### Python Libraries
- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **matplotlib**: Static plotting library
- **plotly**: Interactive visualization library (plotly.express and plotly.graph_objects)
- **sqlite3**: Database connectivity (built-in Python library)
- **datetime**: Date and time handling (built-in Python library)
- **numpy**: Numerical computing support
- **calendar**: Calendar-related utilities (built-in Python library)

### Database
- **SQLite**: Local file-based database for data persistence
- **No external database server required**: Self-contained database solution

### Development Environment
- **Python 3.x**: Runtime environment
- **No external APIs**: Fully self-contained application without third-party service dependencies