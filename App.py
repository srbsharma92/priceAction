#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 21:30:32 2025

@author: saurabhsharma
"""

import streamlit as st
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, time
import pytz

def screener():
    country="india"
    tickers="any"
    indexes="any"
    analysis="technical"
  
    country = country.lower()
    
    fields_overview = [
        "name", "description", "update_mode", "close", "currency", "change",
        "volume", "relative_volume_10d_calc", "Recommend.All", "market_cap_basic",
        "price_earnings_ttm", "earnings_per_share_diluted_ttm",
        "earnings_per_share_diluted_yoy_growth_ttm", "dividends_yield_current",
        "sector", "exchange"
    ]
    
    fields_performance = [
        "name", "description", "update_mode", "close", "currency", "change",
        "Perf.W", "Perf.1M", "Perf.3M", "Perf.6M", "Perf.YTD", "Perf.Y", "Perf.5Y",
        "Perf.10Y", "Perf.All", "Volatility.W", "Volatility.M", "sector", "exchange"
    ]
    
    fields_premarket_postmarket = [
        "name", "description", "update_mode", "premarket_close", "currency",
        "premarket_change", "premarket_gap", "premarket_volume", "close", "change",
        "gap", "volume", "volume|5", "volume|15", "volume_change", "postmarket_close",
        "postmarket_change", "postmarket_volume", "exchange"
    ]
    
    fields_valuation = [
        "name", "description", "update_mode", "market_cap_basic", "fundamental_currency_code",
        "Perf.1Y.MarketCap", "price_earnings_ttm", "price_earnings_growth_ttm",
        "price_sales_current", "price_book_fq", "price_to_cash_f_operating_activities_ttm",
        "price_free_cash_flow_ttm", "price_to_cash_ratio", "enterprise_value_current",
        "enterprise_value_to_revenue_ttm", "enterprise_value_to_ebit_ttm",
        "enterprise_value_ebitda_ttm", "exchange"
    ]
    
    fields_financial = [
        "name", "description", "update_mode", "logoid", "update_mode", "type",
        "typespecs", "total_revenue_ttm", "fundamental_currency_code", "total_revenue_yoy_growth_ttm",
        "gross_profit_ttm", "oper_income_ttm", "net_income_ttm", "ebitda_ttm",
        "earnings_per_share_diluted_ttm", "earnings_per_share_diluted_yoy_growth_ttm",
        "exchange", "gross_margin_ttm", "operating_margin_ttm", "pre_tax_margin_ttm",
        "net_margin_ttm", "free_cash_flow_margin_ttm", "return_on_assets_fq",
        "return_on_equity_fq", "return_on_invested_capital_fq", "research_and_dev_ratio_ttm",
        "sell_gen_admin_exp_other_ratio_ttm"
    ]
    
    fields_technical = [
        "name", "change", "change|5", "volume_change|5", "change|15", "volume_change|15",
        "ATR|60", "low|60", "high|60", "RSI|60",
        "close|60", "EMA10|60", "EMA20|60", "EMA200|60", "EMA10", "EMA20", "EMA200",
        "close", 'volume','gap','volume|5',
        "exchange"
    ]
    
    fields_dict = {
        "overview": fields_overview,
        "performance": fields_performance,
        "premarket_postmarket": fields_premarket_postmarket,
        "valuation": fields_valuation,
        "financial": fields_financial,
        "technical": fields_technical
    }
    
    cols = fields_dict.get(analysis, fields_technical)
    
    query = {
        "markets": [country],
        "symbols": {
            "query": {"types": []},
            "tickers": []
        },
        "options": {"lang": "en"},
        "columns": cols,
        "sort": {
            "sortBy": "market_cap_basic",
            "sortOrder": "desc"
        },
        "range": []
    }
    
    if indexes.lower() != "any":
        query["symbols"]["symbolset"] = [f"SYML:{indexes}"]
    
    if tickers.lower() != "any":
        if isinstance(tickers, str):
            query["symbols"]["tickers"] = [tickers]
        elif isinstance(tickers, list):
            query["symbols"]["tickers"] = tickers
    
    if isinstance(country, list) and len(country) > 1:
        url = "https://scanner.tradingview.com/global/scan"
    else:
        url = f"https://scanner.tradingview.com/{country}/scan"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(query), timeout=20)
    
    if response.status_code != 200:
        st.error(f"Request failed with status: {response.status_code} {response.reason}")
        return None
    
    y = response.json()
    
    def process_d_list(d_list):
        return [x if x is not None else None for x in d_list]
    
    data_list = [process_d_list(item["d"]) for item in y.get("data", [])]
    
    ## various filters
    
    df = pd.DataFrame(data_list, columns=cols)
    df = df[df['exchange'] == 'NSE']
    # Fliters for lighter data
    df=df[ (df['close']>60) & (df['close']<10000)] #price filter

    
    #EMAs metrics
    df['close_EMA10_1H'] = ((100 * (df['close|60'] - df['EMA10|60']) / df['EMA10|60'])).round(2)
    df['close_EMA20_1H'] = ((100 * (df['close|60'] - df['EMA20|60']) / df['EMA20|60'])).round(2)
    df['close_DEMA10'] = ((100 * (df['close|60'] - df['EMA10']) / df['EMA10'])).round(2)
    df['opening'] = ((100 * (df['close'] - df['close|60']) / df['close|60'])).round(2)
    
    # Filter for the F&O Stocks only
    
    # Read the Excel file into a pandas DataFrame
    #fo_list = pd.read_excel('FnO list.xlsx',sheet_name='nse FnO')
    fo_list1=['AARTIIND','ABB','ADANIENT','ADANIPORTS','ABCAPITAL','ABFRL','ALKEM','AMBUJACEM','APOLLOHOSP','ASHOKLEY','ASIANPAINT','ASTRAL','AUBANK','AUROPHARMA','AXISBANK','BAJAJ-AUTO','BAJFINANCE','BAJAJFINSV','BALKRISIND','BANDHANBNK','BANKBARODA','BEL','BHARATFORG','BHEL','BPCL','BHARTIARTL','BIOCON','BSOFT','BOSCHLTD','BRITANNIA','CANBK','CHAMBLFERT','CHOLAFIN','CIPLA','COALINDIA','COFORGE','COLPAL','CONCOR','CROMPTON','CUMMINSIND','DABUR','DALBHARAT','DIVISLAB','DIXON','DLF','DRREDDY','EICHERMOT','EXIDEIND','GAIL','GLENMARK','GODREJCP','GODREJPROP','GRANULES','GRASIM','HAVELLS','HCLTECH','HDFCAMC','HDFCBANK','HDFCLIFE','HEROMOTOCO','HINDALCO','HAL','HINDCOPPER','HINDPETRO','HINDUNILVR','ICICIBANK','ICICIGI','ICICIPRULI','IDFCFIRSTB','IEX','IOC','IRCTC','IGL','INDUSTOWER','INDUSINDBK','NAUKRI','INFY','INDIGO','ITC','JINDALSTEL','JSWSTEEL','JUBLFOOD','KOTAKBANK','LTF','LT','LAURUSLABS','LICHSGFIN','LTIM','LUPIN','MGL','M&MFIN','M&M','MANAPPURAM','MARICO','MARUTI','MFSL','MPHASIS','MCX','MUTHOOTFIN','NATIONALUM','NESTLEIND','NMDC','NTPC','OBEROIRLTY','ONGC','OFSS','PAGEIND','PERSISTENT','PETRONET','PIIND','PIDILITIND','PEL','POLYCAB','PFC','POWERGRID','PNB','RBLBANK','RECLTD','RELIANCE','MOTHERSON','SBICARD','SBILIFE','SHREECEM','SHRIRAMFIN','SIEMENS','SRF','SBIN','SAIL','SUNPHARMA','SYNGENE','TATACHEM','TATACOMM','TCS','TATACONSUM','TATAMOTORS','TATAPOWER','TATASTEEL','TECHM','FEDERALBNK','INDHOTEL','TITAN','TORNTPHARM','TRENT','TVSMOTOR','ULTRACEMCO','UNITDSPR','UPL','VEDL','IDEA','VOLTAS','WIPRO','ZYDUSLIFE','360ONE','ADANIENSOL','ADANIGREEN','AMBER','ANGELONE','APLAPOLLO','ATGL','BANKINDIA','BANKNIFTY','BDL','BLUESTARCO','BSE','CAMS','CDSL','CESC','CGPOWER','CYIENT','DELHIVERY','DMART','ETERNAL','FINNIFTY','FORTIS','GMRAIRPORT','HFCL','HINDZINC','HUDCO','IIFL','INDIANB','INOXWIND','IRB','IREDA','IRFC','JIOFIN','JSL','JSWENERGY','KALYANKJIL','KAYNES','KEI','KFINTECH','KPITTECH','LICI','LODHA','MANKIND','MAXHEALTH','MAZDOCK','MIDCPNIFTY','NBCC','NCC','NHPC','NIFTY','NYKAA','OIL','PATANJALI','PAYTM','PGEL','PHOENIXLTD','PNBHOUSING','POLICYBZR','POONAWALLA','PPLPHARMA','PRESTIGE','RVNL','SJVN','SOLARINDS','SONACOMS','SUPREMEIND','TATAELXSI','TATATECH','TIINDIA','TITAGARH','TORNTPOWER','UNIONBANK','UNOMINDA','VBL','YESBANK']
    
    # Extract a specific column as a list
    #fo_list1 = fo_list['SYMBOL'].tolist()
    if fo_checkbox :
        df = df[df['name'].isin(fo_list1)].sort_values(by='close_EMA10_1H', ascending=False)
    
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    
   #5m charting
    df_5m_Price= df[ (df['change|5'].abs() > 0.7) & ( (df['volume|5']*df['close']) > 1000000)].sort_values(by='change|5', ascending=False)
    df_5m_Price['Momentum']=  np.where(df_5m_Price['change|5'] > 0, 'Bullish','Bearish')
    df_5m_Price=df_5m_Price[['name','change|5','Momentum']]
    df_5m_Price.columns=['Stock Name','Price Change% in 5mins','Momentum']
    
    df_5m_Vol= df[ (df['volume_change|5'] > 200 ) & ( (df['volume|5']*df['close']) > 1000000) ].sort_values(by='volume_change|5', ascending=False)
    df_5m_Vol['Momentum']=  np.where(df_5m_Vol['change|5'] > 0, 'Bullish','Bearish')
    df_5m_Vol['Traded Value']=df_5m_Vol['close']* df_5m_Vol['volume']
    df_5m_Vol=df_5m_Vol[['name','change|5','volume_change|5','Momentum','Traded Value']]
    
    #Presentation
    df_5m_Vol['Traded Value'] = (df_5m_Vol['Traded Value'] / 10000000).round(2).astype(str) + 'Cr'
    df_5m_Vol.columns=['Stock Name','Price Change% in 5mins','Volume Change% in 5mins','Momentum','Days Traded Value']
    
    #opening
    df_opening= df[df['gap'].abs() > 2 ].sort_values(by='gap', ascending=False)
    df_opening['gap']=df_opening['gap'].round(1)
    df_opening['Momentum']=  np.where(df_opening['gap'] > 0, 'Bullish','Bearish')
    df_opening=df_opening[['name','gap','Momentum']]
    df_opening.columns=['Stock Name','Opening Gap','Momentum']
    
    return df, df_5m_Price,df_5m_Vol,df_opening


#Funtion to highlist Bulish=Green & Bearish = Red
def highlight_close(row):
    if row['Momentum'] == 'Bullish':
        return ['background-color: #d4edda; color: green;'] * len(row)
    elif row['Momentum']  == 'Bearish':
        return ['background-color: #f8d7da; color: red;'] * len(row)
    else:
        return ''



# Streamlit UI part

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f4f8;
        color: #333333;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
     """
     <h1 style='text-align: center; color:#4B8BBE;'>Live Price Action in NSE - Free NOW</h1>
     <h3 style='text-align: center; color: gray;'>Where the Smart Money of BIG Fund houses going !!</h3>
     """,
     unsafe_allow_html=True,
)


col1, col2 = st.columns([1, 1])  # Two equal-width columns

with col1:
    refresh = st.button("Refresh")
    
with col2:
    fo_checkbox = st.checkbox("Only F&O Stocks", value=True)
    
# Add this after your main header markdown
utc_now = datetime.utcnow()
ist_tz = pytz.timezone('Asia/Kolkata')
ist_time = utc_now.replace(tzinfo=pytz.utc).astimezone(ist_tz)
current_time = ist_time.strftime("%H:%M:%S %d%b%y")
st.markdown(f"<p style='text-align: center; color: gray;'>Updated At (IST): {current_time}  </p>", unsafe_allow_html=True)

if refresh:

    with st.spinner("Loading data..."):
        df_output, df_output_5mP,df_output_5mVol,df_output_open = screener()
    if df_output_5mP is not None and not df_output_5mP.empty:
        st.subheader("Price Momentum in last 5mins")
        df_output_5mP=df_output_5mP.style.apply(highlight_close,  axis=1)
        st.dataframe(df_output_5mP)
    if df_output_5mVol is not None and not df_output_5mVol.empty:
        st.subheader("Volume Momentum in last 5mins")
        df_output_5mVol=df_output_5mVol.style.apply(highlight_close, axis=1)
        st.dataframe(df_output_5mVol)
    if df_output_open is not None and not df_output_open.empty:
        st.subheader("Pre-Open Momentum")
        df_output_open=df_output_open.style.apply(highlight_close, axis=1)
        st.dataframe(df_output_open)
      
st.markdown(
    """
    <h6 style='text-align: center; color: gray;'> "All a person needs to do is observe what the market is telling him & evaluate it"-Jesse Livermore</h6>
    <h3 style='text-align: center; color:#25AD91;'>Developed by Saurabh Sharma</h3>
    <p style='text-align: center;font-size: 16px; '><a href='mailto:srb_sharma@outlook.com' style='text-align: center;'>Contact @ srb_sharma@outlook.com</a></p>

    <p style='text-align: right; font-size: 11px; font-style: italic; color: gray;'>**Only Stocks with Traded value above 10L</p>
 
    """,
    unsafe_allow_html=True,
)
