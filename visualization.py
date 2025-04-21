import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


def create_spending_pie_chart(transactions_df):
    """
    Create a pie chart showing spending by category.
    
    Args:
        transactions_df: Pandas DataFrame with transaction data
        
    Returns:
        plotly.graph_objects.Figure: Pie chart figure
    """
    # Filter for expenses only (negative amounts)
    expenses_df = transactions_df[transactions_df['amount'] < 0].copy()
    expenses_df['amount'] = expenses_df['amount'].abs(
    )  # Convert to positive for visualization

    # Group by category and sum amounts
    category_totals = expenses_df.groupby(
        'category')['amount'].sum().reset_index()

    # Create pie chart
    fig = px.pie(category_totals,
                 values='amount',
                 names='category',
                 title='Expenses by Category',
                 hole=0.4,
                 color_discrete_sequence=px.colors.qualitative.Plotly)

    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(legend=dict(
        orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5))

    return fig


def create_spending_trend_chart(transactions_df):
    """
    Create a line chart showing spending trends over time.
    
    Args:
        transactions_df: Pandas DataFrame with transaction data
        
    Returns:
        plotly.graph_objects.Figure: Line chart figure
    """
    # Ensure date column is datetime
    if 'date' in transactions_df.columns:
        transactions_df['date'] = pd.to_datetime(transactions_df['date'])

    # Group by month and category
    transactions_df['month'] = transactions_df['date'].dt.to_period('M')

    # Separate income and expenses
    income_df = transactions_df[transactions_df['amount'] > 0].copy()
    expenses_df = transactions_df[transactions_df['amount'] < 0].copy()
    expenses_df['amount'] = expenses_df['amount'].abs(
    )  # Convert to positive for visualization

    # Create monthly summary
    monthly_expenses = expenses_df.groupby(['month', 'category'
                                            ])['amount'].sum().reset_index()
    monthly_income = income_df.groupby('month')['amount'].sum().reset_index()

    # Convert period to string for plotting
    monthly_expenses['month_str'] = monthly_expenses['month'].astype(str)
    monthly_income['month_str'] = monthly_income['month'].astype(str)

    # Create figure
    fig = go.Figure()

    # Add income line
    fig.add_trace(
        go.Scatter(x=monthly_income['month_str'],
                   y=monthly_income['amount'],
                   mode='lines+markers',
                   name='Income',
                   line=dict(color='green', width=3)))

    # Add expense lines for each category
    for category in monthly_expenses['category'].unique():
        category_data = monthly_expenses[monthly_expenses['category'] ==
                                         category]
        fig.add_trace(
            go.Scatter(
                x=category_data['month_str'],
                y=category_data['amount'],
                mode='lines+markers',
                name=category,
                stackgroup='expenses'  # Stack the expenses
            ))

    # Update layout
    fig.update_layout(title='Monthly Income and Expenses Over Time',
                      xaxis_title='Month',
                      yaxis_title='Amount ($)',
                      hovermode='x unified',
                      legend=dict(orientation="h",
                                  yanchor="bottom",
                                  y=-0.5,
                                  xanchor="center",
                                  x=0.5))

    return fig


def create_budget_comparison_chart(transactions_df, budget_df):
    """
    Create a bar chart comparing actual spending to budgeted amounts.
    
    Args:
        transactions_df: Pandas DataFrame with transaction data
        budget_df: Pandas DataFrame with budget data
        
    Returns:
        plotly.graph_objects.Figure: Bar chart figure
    """
    # Filter for expenses only (negative amounts)
    expenses_df = transactions_df[transactions_df['amount'] < 0].copy()
    expenses_df['amount'] = expenses_df['amount'].abs(
    )  # Convert to positive for visualization

    # Group by category and sum amounts
    actual_spending = expenses_df.groupby(
        'category')['amount'].sum().reset_index()

    # Merge with budget data
    comparison_df = pd.merge(actual_spending,
                             budget_df,
                             on='category',
                             how='outer').fillna(0)
    comparison_df.columns = ['Category', 'Actual', 'Budgeted']

    # Calculate difference
    comparison_df[
        'Difference'] = comparison_df['Budgeted'] - comparison_df['Actual']
    comparison_df['Status'] = comparison_df['Difference'].apply(
        lambda x: 'Under Budget' if x >= 0 else 'Over Budget')

    # Create comparison chart
    fig = px.bar(comparison_df,
                 x='Category',
                 y=['Actual', 'Budgeted'],
                 barmode='group',
                 title='Budget vs. Actual Spending',
                 labels={
                     'value': 'Amount ($)',
                     'variable': ''
                 },
                 color_discrete_map={
                     'Actual': '#636EFA',
                     'Budgeted': '#00CC96'
                 })

    fig.update_layout(legend=dict(
        orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5))

    return fig


def create_savings_goal_progress(savings_goal, current_savings):
    """
    Create a gauge chart showing progress towards a savings goal.
    
    Args:
        savings_goal: Target savings amount
        current_savings: Current savings amount
        
    Returns:
        plotly.graph_objects.Figure: Gauge chart figure
    """
    percentage = min(100, (current_savings / savings_goal) *
                     100) if savings_goal > 0 else 0

    fig = go.Figure(
        go.Indicator(mode="gauge+number+delta",
                     value=current_savings,
                     domain={
                         'x': [0, 1],
                         'y': [0, 1]
                     },
                     title={'text': "Progress to Savings Goal"},
                     delta={
                         'reference': savings_goal,
                         'increasing': {
                             'color': "green"
                         }
                     },
                     gauge={
                         'axis': {
                             'range': [0, savings_goal],
                             'tickwidth': 1,
                             'tickcolor': "darkblue"
                         },
                         'bar': {
                             'color': "darkblue"
                         },
                         'bgcolor':
                         "white",
                         'borderwidth':
                         2,
                         'bordercolor':
                         "gray",
                         'steps': [{
                             'range': [0, savings_goal * 0.5],
                             'color': 'red'
                         }, {
                             'range':
                             [savings_goal * 0.5, savings_goal * 0.75],
                             'color':
                             'yellow'
                         }, {
                             'range': [savings_goal * 0.75, savings_goal],
                             'color': 'green'
                         }],
                         'threshold': {
                             'line': {
                                 'color': "red",
                                 'width': 4
                             },
                             'thickness': 0.75,
                             'value': savings_goal
                         }
                     }))

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
    )

    return fig
