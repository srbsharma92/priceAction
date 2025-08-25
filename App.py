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
from datetime import datetime, time

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
        "close", 
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
    
    #EMAs metrics
    df['close_EMA10_1H'] = ((100 * (df['close|60'] - df['EMA10|60']) / df['EMA10|60'])).round(2)
    df['close_EMA20_1H'] = ((100 * (df['close|60'] - df['EMA20|60']) / df['EMA20|60'])).round(2)
    df['close_DEMA10'] = ((100 * (df['close|60'] - df['EMA10']) / df['EMA10'])).round(2)
    df['opening'] = ((100 * (df['close'] - df['close|60']) / df['close|60'])).round(2)
    
    # Filter for the F&O Stocks only
    
    # Read the Excel file into a pandas DataFrame
    fo_list = pd.read_excel('/Users/saurabhsharma/SBC Docs/SSMarketTool/data/FnO list.xlsx',sheet_name='nse FnO')
    
    # Extract a specific column as a list
    fo_list1 = fo_list['SYMBOL'].tolist()
    if fo_checkbox :
        df = df[df['name'].isin(fo_list1)].sort_values(by='close_EMA10_1H', ascending=False)
    
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')
        
    
    #5m charting
    df_5m_Price= df[df['change|5'].abs() > 0.5 ].sort_values(by='change|5', ascending=False)
    df_5m_Vol= df[ (df['volume_change|5'] > 50 ) | (df['volume_change|15']> 50) ].sort_values(by='volume_change|5', ascending=False)
    
    #opening
    df_opening= df[df['opening'].abs() > 0.4 ].sort_values(by='opening', ascending=False)
    if datetime.now().time() > time(9, 35) :
        df_opening =pd.DataFrame()
    
    return df, df_5m_Price,df_5m_Vol,df_opening

# Streamlit UI part

st.title("SaurabhSharma Stock Market Tool")

fo_checkbox = st.checkbox("F&O", value=True)


if st.button("Refresh"):

    with st.spinner("Loading data..."):
        df_output, df_output_5mP,df_output_5mVol,df_output_open = screener()
    if df_output_open is not None and not df_output_open.empty:
        df_output_open=df_output_open[['opening' ] + [col for col in df_output.columns if col not in ['opening' ] ]]
        st.subheader("Opening Momentum")
        st.dataframe(df_output_open)
    if df_output_5mP is not None and not df_output_5mP.empty:
        st.subheader("Price Momentum in last 5mins")
        st.dataframe(df_output_5mP)
    if df_output_5mVol is not None and not df_output_5mVol.empty:
        st.subheader("Volume Momentum in last 5mins")
        st.dataframe(df_output_5mVol)
    if df_output is not None and not df_output.empty:
        first_col=['name','close_EMA10_1H','close_EMA20_1H','close_DEMA10']
        new_order = first_col + [col for col in df_output.columns if col not in first_col]
        df_output = df_output[new_order]
        st.subheader("All Scripts")
        st.dataframe(df_output)
    else:
        st.write("No data found or error occurred.")
