import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import database
import utils

# Initialize database
database.init_db()

# Page configuration
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'refresh' not in st.session_state:
    st.session_state.refresh = 0

def main():
    st.title("💰 Expense Tracker")
    st.markdown("Track your expenses, manage budgets, and analyze spending patterns")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["Dashboard", "Add Expense", "Manage Expenses", "Budget Management", "Analytics", "Export Data"]
        )
    
    # Route to different pages
    if page == "Dashboard":
        show_dashboard()
    elif page == "Add Expense":
        add_expense_page()
    elif page == "Manage Expenses":
        manage_expenses_page()
    elif page == "Budget Management":
        budget_management_page()
    elif page == "Analytics":
        analytics_page()
    elif page == "Export Data":
        export_data_page()

def show_dashboard():
    st.header("📊 Dashboard")
    
    # Get current month data
    current_month = datetime.now().strftime("%Y-%m")
    expenses_df = database.get_expenses()
    budgets_df = database.get_budgets()
    
    if expenses_df.empty:
        st.info("No expenses recorded yet. Start by adding your first expense!")
        return
    
    # Filter current month expenses
    expenses_df['date'] = pd.to_datetime(expenses_df['date'])
    current_month_expenses = expenses_df[
        expenses_df['date'].dt.strftime("%Y-%m") == current_month
    ]
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_spent = current_month_expenses['amount'].sum()
        st.metric("This Month Spent", f"${total_spent:.2f}")
    
    with col2:
        total_budget = budgets_df['amount'].sum() if not budgets_df.empty else 0
        st.metric("Total Budget", f"${total_budget:.2f}")
    
    with col3:
        remaining_budget = total_budget - total_spent
        st.metric("Remaining Budget", f"${remaining_budget:.2f}")
    
    with col4:
        num_transactions = len(current_month_expenses)
        st.metric("Transactions", num_transactions)
    
    # Budget progress bars
    if not budgets_df.empty:
        st.subheader("Budget Progress")
        for _, budget in budgets_df.iterrows():
            category_spent = current_month_expenses[
                current_month_expenses['category'] == budget['category']
            ]['amount'].sum()
            
            progress = min(category_spent / budget['amount'], 1.0) if budget['amount'] > 0 else 0
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{budget['category']}**")
                st.progress(progress)
                st.write(f"${category_spent:.2f} / ${budget['amount']:.2f}")
            with col2:
                if progress > 0.9:
                    st.error("⚠️ Near limit")
                elif progress > 1.0:
                    st.error("🚫 Over budget")
                else:
                    st.success("✅ On track")
    
    # Recent expenses
    st.subheader("Recent Expenses")
    recent_expenses = expenses_df.head(10)
    if not recent_expenses.empty:
        st.dataframe(
            recent_expenses[['date', 'description', 'category', 'amount']].sort_values('date', ascending=False),
            use_container_width=True
        )

def add_expense_page():
    st.header("➕ Add New Expense")
    
    with st.form("add_expense_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            description = st.text_input("Description", placeholder="e.g., Grocery shopping")
            amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
            date = st.date_input("Date", datetime.now())
        
        with col2:
            # Get existing categories for dropdown
            existing_categories = database.get_categories()
            category_options = existing_categories + ["Other"]
            
            category = st.selectbox("Category", category_options)
            if category == "Other":
                category = st.text_input("New Category Name")
            
            notes = st.text_area("Notes (Optional)")
        
        submitted = st.form_submit_button("Add Expense", type="primary")
        
        if submitted:
            if description and amount > 0 and category:
                try:
                    database.add_expense(description, amount, category, date.strftime("%Y-%m-%d"), notes)
                    st.success("Expense added successfully!")
                    st.session_state.refresh += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding expense: {str(e)}")
            else:
                st.error("Please fill in all required fields.")

def manage_expenses_page():
    st.header("📝 Manage Expenses")
    
    # Get all expenses
    expenses_df = database.get_expenses()
    
    if expenses_df.empty:
        st.info("No expenses to manage yet.")
        return
    
    # Filters
    st.subheader("Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ["All"] + database.get_categories()
        selected_category = st.selectbox("Category", categories)
    
    with col2:
        min_amount = st.number_input("Minimum Amount", min_value=0.0, value=0.0)
        max_amount = st.number_input("Maximum Amount", min_value=0.0, value=10000.0)
    
    with col3:
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            max_value=datetime.now()
        )
    
    # Apply filters
    filtered_df = expenses_df.copy()
    filtered_df['date'] = pd.to_datetime(filtered_df['date'])
    
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    filtered_df = filtered_df[
        (filtered_df['amount'] >= min_amount) & 
        (filtered_df['amount'] <= max_amount)
    ]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['date'] >= pd.Timestamp(start_date)) & 
            (filtered_df['date'] <= pd.Timestamp(end_date))
        ]
    
    # Display expenses
    st.subheader(f"Expenses ({len(filtered_df)} found)")
    
    if not filtered_df.empty:
        # Edit/Delete expenses
        for idx, expense in filtered_df.iterrows():
            with st.expander(f"{expense['description']} - ${expense['amount']:.2f} ({expense['date'].strftime('%Y-%m-%d')})"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Category:** {expense['category']}")
                    st.write(f"**Notes:** {expense['notes'] if expense['notes'] else 'None'}")
                
                with col2:
                    if st.button("Edit", key=f"edit_{expense['id']}"):
                        edit_expense(expense)
                
                with col3:
                    if st.button("Delete", key=f"delete_{expense['id']}", type="secondary"):
                        if st.confirm("Are you sure you want to delete this expense?"):
                            database.delete_expense(expense['id'])
                            st.success("Expense deleted!")
                            st.rerun()

def edit_expense(expense):
    st.subheader(f"Edit Expense: {expense['description']}")
    
    with st.form(f"edit_form_{expense['id']}"):
        description = st.text_input("Description", value=expense['description'])
        amount = st.number_input("Amount ($)", value=float(expense['amount']), min_value=0.01, step=0.01)
        
        existing_categories = database.get_categories()
        category_index = existing_categories.index(expense['category']) if expense['category'] in existing_categories else 0
        category = st.selectbox("Category", existing_categories, index=category_index)
        
        date = st.date_input("Date", value=pd.to_datetime(expense['date']).date())
        notes = st.text_area("Notes", value=expense['notes'] if expense['notes'] else "")
        
        if st.form_submit_button("Update Expense"):
            try:
                database.update_expense(
                    expense['id'], description, amount, category, 
                    date.strftime("%Y-%m-%d"), notes
                )
                st.success("Expense updated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating expense: {str(e)}")

def budget_management_page():
    st.header("💼 Budget Management")
    
    # Add/Edit Budget
    st.subheader("Set Monthly Budget")
    
    with st.form("budget_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            categories = database.get_categories()
            if not categories:
                st.warning("Add some expenses first to create categories.")
                return
            
            category = st.selectbox("Category", categories)
            budget_amount = st.number_input("Budget Amount ($)", min_value=0.01, step=1.00)
        
        with col2:
            budget_period = st.selectbox("Period", ["Monthly", "Weekly"])
            description = st.text_area("Description (Optional)")
        
        if st.form_submit_button("Set/Update Budget"):
            if category and budget_amount > 0:
                try:
                    database.set_budget(category, budget_amount, budget_period, description)
                    st.success(f"Budget set for {category}: ${budget_amount:.2f}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error setting budget: {str(e)}")
    
    # Display Current Budgets
    st.subheader("Current Budgets")
    budgets_df = database.get_budgets()
    
    if not budgets_df.empty:
        for _, budget in budgets_df.iterrows():
            with st.expander(f"{budget['category']} - ${budget['amount']:.2f} ({budget['period']})"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if budget['description']:
                        st.write(f"**Description:** {budget['description']}")
                    st.write(f"**Period:** {budget['period']}")
                    st.write(f"**Amount:** ${budget['amount']:.2f}")
                
                with col2:
                    if st.button("Delete", key=f"delete_budget_{budget['id']}"):
                        database.delete_budget(budget['id'])
                        st.success("Budget deleted!")
                        st.rerun()
    else:
        st.info("No budgets set yet.")

def analytics_page():
    st.header("📈 Analytics & Reports")
    
    expenses_df = database.get_expenses()
    
    if expenses_df.empty:
        st.info("No expense data available for analysis.")
        return
    
    expenses_df['date'] = pd.to_datetime(expenses_df['date'])
    
    # Time period selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=90))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Filter data by date range
    mask = (expenses_df['date'] >= pd.Timestamp(start_date)) & (expenses_df['date'] <= pd.Timestamp(end_date))
    filtered_df = expenses_df.loc[mask]
    
    if filtered_df.empty:
        st.warning("No data available for the selected date range.")
        return
    
    # Key Statistics
    st.subheader("Key Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_spent = filtered_df['amount'].sum()
        st.metric("Total Spent", f"${total_spent:.2f}")
    
    with col2:
        avg_daily = total_spent / max(1, (end_date - start_date).days)
        st.metric("Daily Average", f"${avg_daily:.2f}")
    
    with col3:
        num_transactions = len(filtered_df)
        st.metric("Transactions", num_transactions)
    
    with col4:
        avg_transaction = filtered_df['amount'].mean()
        st.metric("Avg Transaction", f"${avg_transaction:.2f}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Category pie chart
        st.subheader("Spending by Category")
        category_totals = filtered_df.groupby('category')['amount'].sum()
        
        fig_pie = px.pie(
            values=category_totals.values, 
            names=category_totals.index,
            title="Expense Distribution by Category"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Monthly spending trend
        st.subheader("Monthly Spending Trend")
        monthly_spending = filtered_df.groupby(filtered_df['date'].dt.to_period('M'))['amount'].sum()
        
        fig_line = px.line(
            x=monthly_spending.index.astype(str),
            y=monthly_spending.values,
            title="Monthly Spending Trend"
        )
        fig_line.update_layout(xaxis_title="Month", yaxis_title="Amount ($)")
        st.plotly_chart(fig_line, use_container_width=True)
    
    # Daily spending pattern
    st.subheader("Daily Spending Pattern")
    daily_spending = filtered_df.groupby('date')['amount'].sum().reset_index()
    
    fig_daily = px.bar(
        daily_spending, 
        x='date', 
        y='amount',
        title="Daily Spending"
    )
    fig_daily.update_layout(xaxis_title="Date", yaxis_title="Amount ($)")
    st.plotly_chart(fig_daily, use_container_width=True)
    
    # Top expenses
    st.subheader("Top 10 Expenses")
    top_expenses = filtered_df.nlargest(10, 'amount')[['date', 'description', 'category', 'amount']]
    st.dataframe(top_expenses, use_container_width=True)

def export_data_page():
    st.header("📤 Export Data")
    
    expenses_df = database.get_expenses()
    budgets_df = database.get_budgets()
    
    if expenses_df.empty:
        st.info("No data available to export.")
        return
    
    # Export options
    st.subheader("Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_type = st.selectbox("Data to Export", ["Expenses", "Budgets", "Both"])
        date_filter = st.checkbox("Filter by Date Range")
        
        if date_filter:
            start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
            end_date = st.date_input("End Date", value=datetime.now())
    
    with col2:
        file_format = st.selectbox("File Format", ["CSV", "JSON"])
        include_notes = st.checkbox("Include Notes", value=True)
    
    # Generate export data
    if st.button("Generate Export File"):
        try:
            export_data = {}
            
            if export_type in ["Expenses", "Both"]:
                df_to_export = expenses_df.copy()
                
                if date_filter:
                    df_to_export['date'] = pd.to_datetime(df_to_export['date'])
                    mask = (df_to_export['date'] >= pd.Timestamp(start_date)) & (df_to_export['date'] <= pd.Timestamp(end_date))
                    df_to_export = df_to_export.loc[mask]
                
                if not include_notes:
                    df_to_export = df_to_export.drop('notes', axis=1, errors='ignore')
                
                export_data['expenses'] = df_to_export
            
            if export_type in ["Budgets", "Both"]:
                export_data['budgets'] = budgets_df
            
            # Create download
            if file_format == "CSV":
                if len(export_data) == 1:
                    # Single dataset
                    data_key = list(export_data.keys())[0]
                    csv_data = export_data[data_key].to_csv(index=False)
                    filename = f"{data_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=filename,
                        mime="text/csv"
                    )
                else:
                    # Multiple datasets - create separate downloads
                    for key, df in export_data.items():
                        csv_data = df.to_csv(index=False)
                        filename = f"{key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                        
                        st.download_button(
                            label=f"Download {key.title()} CSV",
                            data=csv_data,
                            file_name=filename,
                            mime="text/csv",
                            key=f"download_{key}"
                        )
            
            elif file_format == "JSON":
                # Convert DataFrames to JSON
                json_data = {}
                for key, df in export_data.items():
                    json_data[key] = df.to_dict('records')
                
                import json
                json_string = json.dumps(json_data, indent=2, default=str)
                filename = f"expense_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                st.download_button(
                    label="Download JSON",
                    data=json_string,
                    file_name=filename,
                    mime="application/json"
                )
            
            st.success("Export file generated successfully!")
            
        except Exception as e:
            st.error(f"Error generating export: {str(e)}")
    
    # Preview data
    st.subheader("Data Preview")
    if export_type in ["Expenses", "Both"]:
        st.write("**Expenses Data:**")
        st.dataframe(expenses_df.head(), use_container_width=True)
    
    if export_type in ["Budgets", "Both"]:
        st.write("**Budgets Data:**")
        if not budgets_df.empty:
            st.dataframe(budgets_df, use_container_width=True)
        else:
            st.info("No budget data available.")

if __name__ == "__main__":
    main()
