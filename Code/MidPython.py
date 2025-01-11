import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import os
import matplotlib.pyplot as plt
import plotly.express as px

### Page setup ###
st.set_page_config(page_title="Analysis Dashboard", page_icon=":bar_chart:", layout="wide")
st.markdown('<style>div.block-container{padding-top:1.5rem;}</style>',unsafe_allow_html=True) #ปรับ top padding
st.title("Data analysis Dashbord")
# End Page setup #

os.chdir(r"D:\งานเอยใด\Python\Mid_Project\data.csv")
df = pd.read_csv("data.csv",encoding = "ISO-8859-1", dtype={'CustomerID': str,'InvoiceID': str})
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
canceled_products = df[df['InvoiceNo'].str.contains('C', na=False)]

with st.expander("Data Preview"):
    st.markdown(f"Number of data: {len(df):,}")
    st.markdown(f"Number of products that were canceled: {len(canceled_products)}")
    st.dataframe(df)

st.markdown(':rainbow[The cleansed data that was retrieved.]')

variables = '''This dataframe contains 8 variables that correspond to:  
**InvoiceNo**: Invoice number. Nominal, a 6-digit integral number uniquely assigned to each transaction. If this code starts with letter 'c', it indicates a cancellation.  
**StockCode**: Product (item) code. Nominal, a 5-digit integral number uniquely assigned to each distinct product.  
**Description**: Product (item) name. Nominal.  
**Quantity**: The quantities of each product (item) per transaction. Numeric.  
**InvoiceDate**: Invice Date and time. Numeric, the day and time when each transaction was generated.  
**UnitPrice**: Unit price. Numeric, Product price per unit in sterling.  
**CustomerID**: Customer number. Nominal, a 5-digit integral number uniquely assigned to each customer.  
**Country**: Country name. Nominal, the name of the country where each customer resides.
'''
st.markdown(variables)

### Cleaning data ###
df = df.dropna()
df = df.drop_duplicates()

df['TotalSales'] = df['Quantity'] * df['UnitPrice']
canceled_products = df[df['InvoiceNo'].str.contains('C', na=False)]


with st.expander("Cleaned data"):
    st.markdown(f"*Number of orders by members: {len(df):,}*")
    st.markdown(f"Number of products that were canceled: {len(canceled_products)}")
    st.write(df)

csv = df.to_csv().encode("utf-8")
st.download_button(
    label="Download cleaned data as CSV",
    data=csv,
    file_name="Cleaned E-Commerce data.csv",
    mime="text/csv",
)


df_summary = pd.DataFrame([{'products': len(df['StockCode'].value_counts()),    
                    'transactions': len(df['InvoiceNo'].value_counts()),
                    'customers': len(df['CustomerID'].value_counts()),
                    'countries': len(df['Country'].value_counts()) 
            }], columns = ['products', 'transactions', 'customers', 'countries'], index = ['quantity'])
st.dataframe(df_summary)

#--------------------------------------------------------------------------------------------------------------------------

# Choropleth Map Example
temp = df[['CustomerID', 'InvoiceNo', 'Country']].groupby(['CustomerID', 'InvoiceNo', 'Country']).count()
temp = temp.reset_index(drop = False)
countries = temp['Country'].value_counts()

# Define the data for the choropleth map
data = dict(
    type='choropleth',
    locations=countries.index,
    locationmode='country names',
    z=countries,
    text=countries.index,
    colorbar={'title': 'Order nb.'},
    colorscale=[
            [0, 'rgb(230,230,250)'],
            [0.01, 'rgb(166,206,227)'],
            [0.02, 'rgb(31,120,180)'],
            [0.03, 'rgb(178,223,138)'],
            [0.05, 'rgb(51,160,44)'],
            [0.10, 'rgb(251,154,153)'],
            [0.20, 'rgb(255,255,0)'],
            [1, 'rgb(227,26,28)']
    ],
    reversescale=False
)

# Define the layout for the map
layout = dict(
    title='Number of Orders per Country',
    geo=dict(showframe=True, projection={'type': 'mercator'})
)

# Create the figure using plotly.graph_objects
choromap = go.Figure(data=[data], layout=layout)

# Streamlit rendering
st.subheader("Choropleth Map Example")
st.plotly_chart(choromap)

#--------------------------------------------------------------------------------------------------------------------------

# Graph comparing total sales vs canceled sales
totalSales_canceled = canceled_products['TotalSales'].sum()
totalSales_non_canceled = df['TotalSales'].sum()

# Create DataFrame for Comparing
sales_comparison = pd.DataFrame({
    'Status': ['Non-Canceled', 'Canceled'],
    'Total Sales': [totalSales_non_canceled, totalSales_canceled]
})

st.subheader("Comparison of Total Sales")
# graph
fig_bar1 = px.bar(sales_comparison, x='Status',y='Total Sales',text='Total Sales',
                  title="Comparison of Total Sales: Non-Canceled vs Canceled Orders",
                  color='Status',
                  color_discrete_map={'Non-Canceled': 'green', 'Canceled': 'red'}
)
st.plotly_chart(fig_bar1, use_container_width=True)

# download_button
with st.expander("View Data of Comparison of Total Sales:"):
        st.write(sales_comparison.style.background_gradient(cmap = "Blues"))
        csv = sales_comparison.to_csv(index = False).encode("utf-8")
        st.download_button('Download Data' , data = csv , file_name = "Comparison_TotalSales.csv" , mime = 'text/csv')

#--------------------------------------------------------------------------------------------------------------------------

# Table Non-Canceled Orders vs Canceled Orders

cl1 , cl2 = st.columns(2)
with cl1:
    df = df[~df.isin(canceled_products)].dropna()
    st.subheader("Non-Canceled Orders")
    st.write(df)
    st.write(f"*Number of orders by members: {len(df):,}*")

with cl2:
    st.subheader("Canceled Orders")
    st.write(canceled_products)
    st.write(f"Number of products that were canceled: {len(canceled_products)}")

#--------------------------------------------------------------------------------------------------------------------------

# Customer Invoice Summary
st.subheader("Customer Invoice Summary")
df_productCount = df.groupby(by=['InvoiceNo', 'CustomerID'], as_index=False).agg({'InvoiceDate': 'count','Quantity': 'sum'})
df_productCount = df_productCount.rename(columns={'InvoiceDate': 'List Product per Invoice','Quantity': 'Total Quantity Product'})

df_productCount['order_canceled'] = df_productCount['InvoiceNo'].apply(lambda x:int('C' in x))

n1 = df_productCount['order_canceled'].sum()
n2 = df_productCount.shape[0]
st.dataframe(df_productCount , width = 1000)

#--------------------------------------------------------------------------------------------------------------------------

# Filter
st.header("Choose your filter: ")

# Create for Country
country = st.multiselect("Pick your Country", df["Country"].unique())
if not country:
    filtered_df = df.copy()
else:
    filtered_df = df[df["Country"].isin(country)]

#--------------------------------------------------------------------------------------------------------------------------
 
# Start Date & End Date

col1, col2 = st.columns((2))
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

# Getting the min and max date
startDate = pd.to_datetime(df["InvoiceDate"]).min()
endDate = pd.to_datetime(df["InvoiceDate"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["InvoiceDate"] >= date1) & (df["InvoiceDate"] <= date2)].copy()

#--------------------------------------------------------------------------------------------------------------------------

filtered_df['TotalSales'] = df['Quantity'] * df['UnitPrice']

# Country wise Sales
      
st.subheader("Country wise Sales")
cl1, cl2 = st.columns(2)
with cl1:
    fig_pie = px.pie(filtered_df, values = filtered_df['TotalSales'] , names = "Country")
    fig_pie.update_traces(text = filtered_df["Country"] , textposition = "inside")
    st.plotly_chart(fig_pie , use_container_width = True , height = 650)

with cl2:
    with st.expander("Country_wise_Sales ViewData"):
            country = filtered_df.groupby(by = "Country" , as_index = False)['TotalSales'].sum()
            st.write(country.style.background_gradient(cmap = "Oranges"))
            csv = country.to_csv(index = False).encode('utf-8')
            st.download_button("Download Data" , data = csv , file_name = "Country_wise_Sales.csv" , mime = "text/csv",
                                help = 'Click here to download the data as a CSV file')

#--------------------------------------------------------------------------------------------------------------------------

filtered_df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
filtered_df['Date'] = filtered_df['InvoiceDate'].dt.strftime("%Y-%m-%d")
filtered_df['Month'] = filtered_df['InvoiceDate'].dt.to_period('M').astype(str)

# Calculate total daily sales
daily_sales = filtered_df.groupby('Date', as_index=False)['TotalSales'].sum()

# Calculate monthly total sales
monthly_sales = filtered_df.groupby('Month', as_index=False)['TotalSales'].sum()

cl1 , cl2 = st.columns(2)
with cl1:
    st.subheader("Daily Total Sales")

    # graph
    fig_line1 = px.line(daily_sales, x='Date', y='TotalSales', title='Daily Total Sales',
                        labels={"TotalSales": "Amount"}, height=500, width=1000,
                        template="gridon")
    st.plotly_chart(fig_line1, use_container_width=True)

    # download_button
    with st.expander("View Data of Daily Total Sales:"):
        st.write(daily_sales.T.style.background_gradient(cmap = "Blues"))
        csv = daily_sales.to_csv(index = False).encode("utf-8")
        st.download_button('Download Data' , data = csv , file_name = "Daily_TotalSales.csv" , mime = 'text/csv')

with cl2:
    st.subheader("Monthly Total Sales")
    
    # graph
    fig_line2 = px.line(monthly_sales, x='Month', y='TotalSales', title='Monthly Total Sales',
                        labels={"TotalSales": "Amount"}, height=500, width=1000,
                        template="gridon")
    st.plotly_chart(fig_line2, use_container_width=True)
    
    # download_button
    with st.expander("View Data of Monthly Total Sales:"):
        st.write(monthly_sales.T.style.background_gradient(cmap = "Blues"))
        csv = monthly_sales.to_csv(index = False).encode("utf-8")
        st.download_button('Download Data' , data = csv , file_name = "Monthly_TotalSales.csv" , mime = 'text/csv')
    
#--------------------------------------------------------------------------------------------------------------------------

# Sales by Time Period

# Create a function to find a time period
def time_of_day(hour):
    if 6 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 18:
        return 'Afternoon'
    elif 18 <= hour < 24:
        return 'Evening'
    else:
        return 'Night'

# Calculate total sales by time period
filtered_df['TimePeriod'] = filtered_df['InvoiceDate'].dt.hour.apply(time_of_day)
time_period_sales = filtered_df.groupby('TimePeriod' , as_index=False)['TotalSales'].sum()

st.subheader("Sales by Time Period")

# graph
fig_bar2 = px.bar(time_period_sales, x='TimePeriod', y='TotalSales', color='TimePeriod')
st.plotly_chart(fig_bar2, use_container_width=True)

# download_button
with st.expander("View Data of Sales by Time Period:"):
        st.write(time_period_sales.T.style.background_gradient(cmap = "Blues"))
        csv = time_period_sales.to_csv(index = False).encode("utf-8")
        st.download_button('Download Data' , data = csv , file_name = "Sales_by_TimePeriod.csv" , mime = 'text/csv')

#--------------------------------------------------------------------------------------------------------------------------

# Product Sales Summary

st.subheader("Product Sales Summary")

filtered_df_product = filtered_df.groupby(by=['StockCode','Description'], as_index=False).agg({'Quantity': 'sum','TotalSales': 'sum','StockCode' : 'count'})
filtered_df_product = filtered_df_product.rename(columns = {'Quantity': 'Total Quantity','TotalSales': 'TotalSales per Procuct','StockCode' : 'Total orders per product'})

st.dataframe(filtered_df_product, width=1000)

# download_button
with st.expander("View Data of Product Sales Summary:"):
        st.write(filtered_df_product.style.background_gradient(cmap = "Oranges"))
        csv = filtered_df_product.to_csv(index = False).encode("utf-8")
        st.download_button('Download Data' , data = csv , file_name = "ProductSales_Summary.csv" , mime = 'text/csv')


# Top 5

# : Total Quantity
# Select the top 5
top_5_products = filtered_df_product.nlargest(5, 'Total Quantity')

# graph
#st.subheader("Top 5 Products by Total Quantity")
fig_pie2 = px.pie(top_5_products, values = top_5_products['Total Quantity'] , names = 'Description',
                  title = "Top 5 Products by Total Quantity")
fig_pie2.update_traces(text = filtered_df['Description'] , textposition = "outside")
st.plotly_chart(fig_pie2)


# : TotalSales
# Select the top 5
top_5_products = filtered_df_product.nlargest(5, 'TotalSales per Procuct')

# graph
#st.subheader("Top 5 Products by TotalSales per Procuct")
fig_pie2 = px.pie(top_5_products, values = top_5_products['TotalSales per Procuct'] , names = 'Description',
                  title = "Top 5 Products by TotalSales per Procuct")
fig_pie2.update_traces(text = filtered_df['Description'] , textposition = "outside")
st.plotly_chart(fig_pie2)


# : Total orders per product
# Select the top 5
top_5_products = filtered_df_product.nlargest(5, 'Total orders per product')

# graph
#st.subheader("Top 5 Products by Total orders per product")
fig_pie2 = px.pie(top_5_products, values = top_5_products['Total orders per product'] , names = 'Description',
                  title = "Top 5 Products by Total orders per product")
fig_pie2.update_traces(text = filtered_df['Description'] , textposition = "outside")
st.plotly_chart(fig_pie2)

#--------------------------------------------------------------------------------------------------------------------------

# End Main page #
