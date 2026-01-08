#!/usr/bin/env python3
"""
股票技术分析

对股票进行技术分析，计算常用技术指标
"""

import argparse
import sys
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np


def calculate_sma(data, window):
    """计算简单移动平均线 (Simple Moving Average)"""
    return data["Close"].rolling(window=window).mean()


def calculate_ema(data, window):
    """计算指数移动平均线 (Exponential Moving Average)"""
    return data["Close"].ewm(span=window, adjust=False).mean()


def calculate_rsi(data, window=14):
    """计算相对强弱指标 (Relative Strength Index)"""
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(data, fast=12, slow=26, signal=9):
    """
    计算 MACD (Moving Average Convergence Divergence)

    Returns:
        tuple: (MACD线, 信号线, MACD柱)
    """
    ema_fast = data["Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = data["Close"].ewm(span=slow, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    macd_histogram = macd_line - signal_line

    return macd_line, signal_line, macd_histogram


def calculate_bollinger_bands(data, window=20, num_std=2):
    """
    计算布林带 (Bollinger Bands)

    Returns:
        tuple: (上轨, 中轨, 下轨)
    """
    sma = data["Close"].rolling(window=window).mean()
    std = data["Close"].rolling(window=window).std()

    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)

    return upper_band, sma, lower_band


def calculate_atr(data, window=14):
    """计算平均真实范围 (Average True Range)"""
    high_low = data["High"] - data["Low"]
    high_close = np.abs(data["High"] - data["Close"].shift())
    low_close = np.abs(data["Low"] - data["Close"].shift())

    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    atr = true_range.rolling(window=window).mean()

    return atr


def analyze_stock(ticker, period="6mo", indicators=None):
    """
    对股票进行技术分析

    Args:
        ticker: 股票代码
        period: 分析周期
        indicators: 要计算的指标列表

    Returns:
        DataFrame: 包含技术指标的数据
    """
    try:
        # 获取历史数据
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)

        if data.empty:
            print(f"❌ 未找到股票 {ticker} 的数据", file=sys.stderr)
            return None

        # 计算技术指标
        if indicators is None:
            indicators = ["SMA", "EMA", "RSI", "MACD", "BB"]

        if "SMA" in indicators:
            data["SMA_20"] = calculate_sma(data, 20)
            data["SMA_50"] = calculate_sma(data, 50)
            data["SMA_200"] = calculate_sma(data, 200)

        if "EMA" in indicators:
            data["EMA_12"] = calculate_ema(data, 12)
            data["EMA_26"] = calculate_ema(data, 26)

        if "RSI" in indicators:
            data["RSI"] = calculate_rsi(data)

        if "MACD" in indicators:
            macd, signal, histogram = calculate_macd(data)
            data["MACD"] = macd
            data["MACD_Signal"] = signal
            data["MACD_Histogram"] = histogram

        if "BB" in indicators:
            upper, middle, lower = calculate_bollinger_bands(data)
            data["BB_Upper"] = upper
            data["BB_Middle"] = middle
            data["BB_Lower"] = lower

        if "ATR" in indicators:
            data["ATR"] = calculate_atr(data)

        return data

    except Exception as e:
        print(f"❌ 分析失败: {str(e)}", file=sys.stderr)
        return None


def generate_signals(data):
    """
    生成交易信号

    Returns:
        dict: 当前的技术信号
    """
    signals = {}
    latest = data.iloc[-1]
    prev = data.iloc[-2]

    # 趋势信号（基于移动平均线）
    if "SMA_20" in data.columns and "SMA_50" in data.columns:
        if latest["Close"] > latest["SMA_20"] > latest["SMA_50"]:
            signals["趋势"] = "强势上涨 ↑"
        elif latest["Close"] < latest["SMA_20"] < latest["SMA_50"]:
            signals["趋势"] = "强势下跌 ↓"
        elif latest["Close"] > latest["SMA_20"]:
            signals["趋势"] = "短期上涨 ↗"
        elif latest["Close"] < latest["SMA_20"]:
            signals["趋势"] = "短期下跌 ↘"
        else:
            signals["趋势"] = "震荡 ↔"

    # RSI 信号
    if "RSI" in data.columns:
        rsi = latest["RSI"]
        if rsi > 70:
            signals["RSI"] = f"超买 ({rsi:.1f}) ⚠️"
        elif rsi < 30:
            signals["RSI"] = f"超卖 ({rsi:.1f}) ⚠️"
        else:
            signals["RSI"] = f"正常 ({rsi:.1f})"

    # MACD 信号
    if "MACD" in data.columns:
        if (
            latest["MACD"] > latest["MACD_Signal"]
            and prev["MACD"] <= prev["MACD_Signal"]
        ):
            signals["MACD"] = "金叉 (买入信号) ↑"
        elif (
            latest["MACD"] < latest["MACD_Signal"]
            and prev["MACD"] >= prev["MACD_Signal"]
        ):
            signals["MACD"] = "死叉 (卖出信号) ↓"
        elif latest["MACD"] > latest["MACD_Signal"]:
            signals["MACD"] = "多头排列"
        else:
            signals["MACD"] = "空头排列"

    # 布林带信号
    if "BB_Upper" in data.columns:
        if latest["Close"] > latest["BB_Upper"]:
            signals["布林带"] = "突破上轨 (超买) ⚠️"
        elif latest["Close"] < latest["BB_Lower"]:
            signals["布林带"] = "突破下轨 (超卖) ⚠️"
        else:
            signals["布林带"] = "正常区间"

    return signals


def main():
    parser = argparse.ArgumentParser(description="股票技术分析")
    parser.add_argument("--ticker", required=True, help="股票代码")
    parser.add_argument("--period", default="6mo", help="分析周期（默认: 6mo）")
    parser.add_argument(
        "--indicators",
        nargs="+",
        choices=["SMA", "EMA", "RSI", "MACD", "BB", "ATR"],
        help="要计算的指标（默认: SMA EMA RSI MACD BB）",
    )
    parser.add_argument("--output", help="输出文件路径（CSV 格式）")
    parser.add_argument("--signals-only", action="store_true", help="仅显示交易信号")

    args = parser.parse_args()

    print(f"\n📊 股票技术分析: {args.ticker}")
    print("=" * 60)

    # 进行分析
    data = analyze_stock(args.ticker, args.period, args.indicators)

    if data is None:
        return

    print(
        f"\n数据周期: {data.index[0].strftime('%Y-%m-%d')} 至 {data.index[-1].strftime('%Y-%m-%d')}"
    )
    print(f"数据点数量: {len(data)}")

    # 显示当前价格
    latest = data.iloc[-1]
    print(f"\n当前价格: ${latest['Close']:.2f}")

    # 生成并显示交易信号
    print("\n📈 技术信号:")
    signals = generate_signals(data)
    for indicator, signal in signals.items():
        print(f"  {indicator:10}: {signal}")

    if args.signals_only:
        return

    # 显示最新的技术指标值
    print("\n📊 最新技术指标:")
    indicators_to_show = [
        col
        for col in data.columns
        if col
        not in ["Open", "High", "Low", "Close", "Volume", "Dividends", "Stock Splits"]
    ]
    for indicator in indicators_to_show:
        value = latest[indicator]
        if pd.notna(value):
            print(f"  {indicator:20}: {value:.2f}")

    # 显示最近的数据
    print("\n最近 5 个交易日:")
    columns_to_show = ["Close"] + indicators_to_show[:5]  # 只显示部分指标
    print(data[columns_to_show].tail(5).to_string())

    # 保存到文件
    if args.output:
        data.to_csv(args.output)
        print(f"\n✅ 完整数据已保存到: {args.output}")

    print("\n⚠️  免责声明: 技术分析仅供参考，不构成投资建议")
    print("=" * 60)


if __name__ == "__main__":
    main()
