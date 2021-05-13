import streamlit as st
import pandas as pd
import numpy as np

import plotly.graph_objs as go
from plotly.offline import init_notebook_mode, iplot

###################### Page size
#st.set_page_config(layout="wide")
#st.markdown("""
#<style>
#.big-font {
#    font-size:300px !important;
#}
#</style>
#""", unsafe_allow_html=True)
###############################

st.title("Ledger")
st.markdown("* Use sidebar menu for the search criteria.")

#---- Pandas
data =  pd.read_csv('income.csv', delimiter=",")
data['Date'] = pd.to_datetime( data['Date'])

#------ Search input
date_start = st.sidebar.date_input("Start date [yyyy-mm-dd]")
date_end = st.sidebar.date_input("End date [yyyy-mm-dd]")

description_pat= st.sidebar.text_input("Description")

amount_min = st.sidebar.number_input("Amount >=")
amount_max = st.sidebar.number_input("Amount <")

#---- Error in case wrong input.
if date_start > date_end:
    st.error("Wrong search criteria !!!!!!!!! dates ")
elif amount_max < amount_min:
    st.error("Wrong search criteria !!!!!!!!! max_amount < min_amount ")

#---- Select output options
status = st.radio("Select transaction type: ", ('Income', 'Expenditure', 'Both'))

#-------------- Make bool map for the search
bool_map = (data['Date'] >= pd.Timestamp(date_start)) & (data['Date'] <= pd.Timestamp(date_end))
if description_pat != "":
    bool_map = bool_map & (data['Description'].str.lower().str.contains( str.lower(description_pat) ))
if amount_min > 0.0:
    bool_map = bool_map & (data['Amount'] >= amount_min)
if amount_max > 0.0:
    bool_map = bool_map & (data['Amount'] <= amount_max)

#----- Show income and expenditure 
if status == "Income":
    bool_map_temp = bool_map & (data['Type'] == 1)
    df_out = data[bool_map_temp]
elif status== "Expenditure":
    bool_map_temp = bool_map  & (data['Type'] == 0)
    df_out= data[bool_map_temp]
else:
    df_out = data[bool_map]
st.dataframe(df_out)

#---- Total amount
st.markdown("### Total")
sum_income = data[ bool_map & (data['Type'] == 1) ]['Amount'].sum() 
sum_expenditure = data[ bool_map & (data['Type'] == 0) ]['Amount'].sum() 
st.write("Income: ", sum_income )
st.write("Expenditure: ", sum_expenditure )
st.write("Difference: ", sum_income - sum_expenditure  )

#-------- Show the full ledger
if st.checkbox("Show full ledger"):
    st.dataframe(data)
    st.write("Total rows: ", data.shape[0])
    st.write("Total cols: ", data.shape[1])
    st.write("Total NAN : ", data.isna().sum())

#---- Summarize over time-intervals
st.header(" Summary ")
if st.checkbox("Show summary"):
#---- Select summary interval
    summary_over = st.selectbox("Summary over ( Days=D, Weeks, Months=M ", ['D', 'W','M'])

    df_income = data[ bool_map & (data['Type'] == 1) ]
    df_expenditure = data[ bool_map & (data['Type'] == 0) ]

    def summarize(df):
        t_df = df.set_index('Date')
        out_df = t_df.resample(summary_over).sum()
        return out_df

    summary_income = summarize( df_income)
    summary_expenditure = summarize( df_expenditure)

    #---------------------------
    # Plots income
    trace1 = go.Scatter(
                        x = summary_income.index,
                        y = summary_income['Amount'],
                        mode = "lines+markers",
                        name = "Income",
                        marker = dict(color = 'rgba(16, 112, 2, 0.8)'),
                        )

    data = [trace1]
    layout = dict(title = 'Income',
                  xaxis= dict(title= 'Time',ticklen= 5, tickangle = 30, zeroline= False),
                  yaxis= dict(title= 'Amount', ticklen= 5,zeroline= False)
                 )
    fig = dict(data = data, layout = layout)
    st.plotly_chart(fig)

    #---------------------------
    # Plots Expenditure 
    trace2 = go.Scatter(
                        x = summary_expenditure.index,
                        y = summary_expenditure['Amount'],
                        mode = "lines+markers",
                        name = "Expenditure",
                        marker = dict(color = 'rgba(16, 112, 2, 0.8)'),
                        )

    data = [trace2]
    layout = dict(title = 'Expenditure',
                  xaxis= dict(title= 'Time',ticklen= 5, tickangle = 30, zeroline= False),
                  yaxis= dict(title= 'Amount', ticklen= 5,zeroline= False)
                 )
    fig = dict(data = data, layout = layout)
    st.plotly_chart(fig)

#--------
#st.subheader("Checks")
#if st.checkbox("Show"):
#    st.dataframe(summary_income)
#    st.dataframe(summary_expenditure)
