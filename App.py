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
    
    #for col in df.columns:
    #    df[col] = pd.to_numeric(df[col], errors='coerce')
        
    
   #5m charting==============================
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
    
    #15m charting =====================================================
    df_15m_Price= df[ (df['change|15'].abs() > 0.7) & ( (df['volume|5']*df['close']) > 1000000)].sort_values(by='change|15', ascending=False)
    df_15m_Price['Momentum']=  np.where(df_15m_Price['change|15'] > 0, 'Bullish','Bearish')
    df_15m_Price=df_15m_Price[['name','change|15','Momentum']]
    df_15m_Price.columns=['Stock Name','Price Change% in 15mins','Momentum']
     
    df_15m_Vol= df[ (df['volume_change|15'] > 200 ) & ( (df['volume|5']*df['close']) > 1000000) ].sort_values(by='volume_change|15', ascending=False)
    df_15m_Vol['Momentum']=  np.where(df_15m_Vol['change|15'] > 0, 'Bullish','Bearish')
    df_15m_Vol['Traded Value']=df_15m_Vol['close']* df_15m_Vol['volume']
    df_15m_Vol=df_15m_Vol[['name','change|15','volume_change|15','Momentum','Traded Value']]
     
    #Presentation
    df_15m_Vol['Traded Value'] = (df_15m_Vol['Traded Value'] / 10000000).round(2).astype(str) + 'Cr'
    df_15m_Vol.columns=['Stock Name','Price Change% in 15mins','Volume Change% in 15mins','Momentum','Days Traded Value']

    #opening
    df_opening= df[df['gap'].abs() > 2 ].sort_values(by='gap', ascending=False)
    df_opening['gap']=df_opening['gap'].round(1)
    df_opening['Momentum']=  np.where(df_opening['gap'] > 0, 'Bullish','Bearish')
    df_opening=df_opening[['name','gap','Momentum']]
    df_opening.columns=['Stock Name','Opening Gap','Momentum']
    
    return df, df_5m_Price,df_5m_Vol,df_15m_Price,df_15m_Vol,df_opening


#Funtion to highlist Bulish=Green & Bearish = Red
def highlight_close(row):
    if row['Momentum'] == 'Bullish':
        return ['background-color: #d4edda; color: green;'] * len(row)
    elif row['Momentum']  == 'Bearish':
        return ['background-color: #f8d7da; color: red;'] * len(row)
    else:
        return ''


# Purely cosmetic Styler wrapper — chained on top of highlight_close, does not
# alter any values, columns, or the Bullish/Bearish logic itself. Only the
# background_color / color / border-color / font-weight / text-align /
# font-style properties are honored by st.dataframe's Styler support; the
# table_styles (header row) additionally apply when rendered via st.table.
def theme_table(styler):
    return (
        styler
        .set_properties(**{
            'border-color': 'rgba(212,175,55,0.18)',
            'font-weight': '500',
            'text-align': 'center',
        })
        .set_table_styles([
            {
                'selector': 'thead th',
                'props': [
                    ('background-color', '#D4AF37'),
                    ('color', '#0b1420'),
                    ('font-weight', '700'),
                    ('text-transform', 'uppercase'),
                    ('letter-spacing', '0.5px'),
                    ('font-size', '12.5px'),
                    ('text-align', 'center'),
                    ('padding', '10px 12px'),
                    ('border-bottom', '2px solid #B8912C'),
                ]
            },
            {
                'selector': 'tbody td',
                'props': [
                    ('padding', '8px 12px'),
                    ('border-bottom', '1px solid rgba(212,175,55,0.12)'),
                ]
            },
            {
                'selector': 'table',
                'props': [
                    ('border-collapse', 'collapse'),
                    ('width', '100%'),
                ]
            },
        ])
    )



# ============================= Streamlit UI part =============================

st.set_page_config(
    page_title="NSE Live Price Action | Smart Money Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* App background — deep navy finance terminal */
    .stApp {
        background: radial-gradient(circle at top left, #101b2d 0%, #0b1420 45%, #060a12 100%);
        color: #E7ECF3;
    }

    /* Kill default streamlit padding clutter at top */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1150px;
    }

    /* Hero header card */
    .hero-card {
        background: linear-gradient(135deg, rgba(20,33,54,0.95) 0%, rgba(11,20,32,0.95) 100%);
        border: 1px solid rgba(212,175,55,0.35);
        border-radius: 18px;
        padding: 2rem 2.2rem 1.5rem 2.2rem;
        margin-bottom: 1.6rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.45);
        text-align: center;
    }

    .hero-eyebrow {
        letter-spacing: 3px;
        font-size: 12px;
        font-weight: 600;
        color: #D4AF37;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(90deg, #F4E4A6 0%, #D4AF37 45%, #F4E4A6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }

    .hero-subtitle {
        font-size: 1.02rem;
        color: #9DAAC0;
        margin-top: 0.5rem;
        font-weight: 500;
        letter-spacing: 0.3px;
    }

    /* Controls row card */
    .controls-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1rem 1.3rem;
        margin-bottom: 0.6rem;
    }

    /* Timestamp pill */
    .timestamp-pill {
        display: inline-block;
        margin: 0 auto;
        padding: 6px 16px;
        border-radius: 999px;
        background: rgba(212,175,55,0.08);
        border: 1px solid rgba(212,175,55,0.3);
        color: #D4AF37;
        font-size: 12.5px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .timestamp-wrap { text-align: center; margin: 0.4rem 0 1.6rem 0; }

    /* Tabs — restyled to match the navy/gold terminal theme */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(212,175,55,0.2);
        border-radius: 12px;
        padding: 6px;
        margin-top: 1.6rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: auto;
        padding: 10px 20px;
        border-radius: 8px;
        background-color: transparent;
        color: #9DAAC0;
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        font-size: 1.02rem;
        letter-spacing: 0.3px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #D4AF37 0%, #B8912C 100%) !important;
        color: #0b1420 !important;
        box-shadow: 0 4px 14px rgba(212,175,55,0.3);
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.4rem;
    }

    /* Section badges above each table */
    .section-badge {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 1.1rem 0 0.6rem 0;
        padding: 10px 16px;
        border-radius: 10px;
        background: linear-gradient(90deg, rgba(212,175,55,0.12) 0%, rgba(212,175,55,0.02) 100%);
        border-left: 3px solid #D4AF37;
    }
    .section-badge .icon {
        font-size: 20px;
    }
    .section-badge .label {
        font-size: 1.05rem;
        font-weight: 700;
        color: #F0E6C8;
        letter-spacing: 0.2px;
    }

    /* Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #D4AF37 0%, #B8912C 100%);
        color: #0b1420;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        letter-spacing: 0.4px;
        box-shadow: 0 4px 14px rgba(212,175,55,0.25);
        transition: all 0.15s ease-in-out;
        width: 100%;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(212,175,55,0.4);
        color: #0b1420;
    }

    /* Checkbox label styling */
    .stCheckbox label p {
        font-weight: 600 !important;
        color: #E7ECF3 !important;
    }

    /* Table container polish (st.table renders real HTML) */
    [data-testid="stTable"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(212,175,55,0.25);
        box-shadow: 0 6px 18px rgba(0,0,0,0.35);
    }
    [data-testid="stTable"] table {
        background-color: #0F1A2C;
    }
    [data-testid="stTable"] tbody tr:hover td {
        filter: brightness(1.12);
    }

    /* Divider */
    hr {
        border-color: rgba(255,255,255,0.08);
    }

    /* Footer */
    .footer-quote {
        text-align: center;
        color: #8A96AA;
        font-style: italic;
        font-size: 0.92rem;
        margin-top: 2.4rem;
        padding-top: 1.2rem;
        border-top: 1px solid rgba(255,255,255,0.08);
    }
    .footer-name {
        text-align: center;
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        font-size: 1.3rem;
        color: #D4AF37;
        margin-top: 0.4rem;
    }
    .footer-contact a {
        color: #9DAAC0 !important;
        text-decoration: none;
        font-weight: 500;
    }
    .footer-contact a:hover {
        color: #D4AF37 !important;
    }
    .footer-note {
        text-align: right;
        font-size: 11px;
        font-style: italic;
        color: #64708A;
        margin-top: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
     """
     <div class="hero-card">
        <div class="hero-eyebrow">NSE &nbsp;•&nbsp; Institutional Grade Screener</div>
        <div class="hero-title">Live Price Action Terminal</div>
        <div class="hero-subtitle">Track where the Smart Money of Big Fund Houses is moving — in real time</div>
     </div>
     """,
     unsafe_allow_html=True,
)

st.markdown('<div class="controls-card">', unsafe_allow_html=True)
col1, col2 = st.columns([1, 1])  # Two equal-width columns

with col1:
    refresh = st.button("🔄  Refresh Market Data")
    
with col2:
    fo_checkbox = st.checkbox("Only F&O Stocks", value=True)
st.markdown('</div>', unsafe_allow_html=True)
    
# Add this after your main header markdown
utc_now = datetime.utcnow()
ist_tz = pytz.timezone('Asia/Kolkata')
ist_time = utc_now.replace(tzinfo=pytz.utc).astimezone(ist_tz)
current_time = ist_time.strftime("%H:%M:%S %d%b%y")
st.markdown(
    f"<div class='timestamp-wrap'><span class='timestamp-pill'>🕒 Updated At (IST): {current_time}</span></div>",
    unsafe_allow_html=True
)

if refresh:

    with st.spinner("Loading data..."):
        df_output, df_output_5mP,df_output_5mVol,df_output_15mP,df_output_15mVol,df_output_open = screener()

    tab_5m, tab_15m, tab_open = st.tabs(["⏱️ 5 Minutes", "⏳ 15 Minutes", "🔔 Pre-Open Market"])

    # ===================== SECTION 1: 5 MINUTES =====================
    with tab_5m:
        if df_output_5mP is not None and not df_output_5mP.empty:
            st.markdown(
                "<div class='section-badge'><span class='icon'>⚡</span><span class='label'>Price Momentum in Last 5 Mins</span></div>",
                unsafe_allow_html=True
            )
            df_output_5mP=df_output_5mP.style.apply(highlight_close,  axis=1)
            df_output_5mP=theme_table(df_output_5mP)
            st.table(df_output_5mP)
        if df_output_5mVol is not None and not df_output_5mVol.empty:
            st.markdown(
                "<div class='section-badge'><span class='icon'>📊</span><span class='label'>Volume Momentum in Last 5 Mins</span></div>",
                unsafe_allow_html=True
            )
            df_output_5mVol=df_output_5mVol.style.apply(highlight_close, axis=1)
            df_output_5mVol=theme_table(df_output_5mVol)
            st.table(df_output_5mVol)

    # ===================== SECTION 2: 15 MINUTES =====================
    with tab_15m:
        if df_output_15mP is not None and not df_output_15mP.empty:
            st.markdown(
                "<div class='section-badge'><span class='icon'>⚡</span><span class='label'>Price Momentum in Last 15 Mins</span></div>",
                unsafe_allow_html=True
            )
            df_output_15mP=df_output_15mP.style.apply(highlight_close,  axis=1)
            df_output_15mP=theme_table(df_output_15mP)
            st.table(df_output_15mP)
        if df_output_15mVol is not None and not df_output_15mVol.empty:
            st.markdown(
                "<div class='section-badge'><span class='icon'>📊</span><span class='label'>Volume Momentum in Last 15 Mins</span></div>",
                unsafe_allow_html=True
            )
            df_output_15mVol=df_output_15mVol.style.apply(highlight_close, axis=1)
            df_output_15mVol=theme_table(df_output_15mVol)
            st.table(df_output_15mVol)

    # ===================== SECTION 3: PRE-OPEN MARKET =====================
    with tab_open:
        if df_output_open is not None and not df_output_open.empty:
            st.markdown(
                "<div class='section-badge'><span class='icon'>🔔</span><span class='label'>Pre-Open Momentum</span></div>",
                unsafe_allow_html=True
            )
            df_output_open=df_output_open.style.apply(highlight_close, axis=1)
            df_output_open=theme_table(df_output_open)
            st.table(df_output_open)
      
st.markdown(
    """
    <div class="footer-quote">"All a person needs to do is observe what the market is telling him &amp; evaluate it" — Jesse Livermore</div>
    <div class="footer-name">Developed by Saurabh Sharma</div>
    <p class="footer-contact" style='text-align: center;font-size: 15px; margin-top:0.3rem;'><a href='mailto:srb_sharma@outlook.com'>✉️ Contact @ srb_sharma@outlook.com</a></p>
    <p class="footer-note">**Only Stocks with Traded value above 10L</p>
    """,
    unsafe_allow_html=True,
)
