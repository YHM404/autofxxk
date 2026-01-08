#!/usr/bin/env python3
"""
获取股票历史数据

使用 yfinance 获取指定股票的历史价格数据
"""

import argparse
import sys
from datetime import datetime
import yfinance as yf
import pandas as pd


def get_stock_data(ticker, period="1mo", interval="1d", start=None, end=None):
    """
    获取股票历史数据

    Args:
        ticker: 股票代码
        period: 时间周期 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: 数据间隔 (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        start: 开始日期 (YYYY-MM-DD)
        end: 结束日期 (YYYY-MM-DD)

    Returns:
        DataFrame: 股票历史数据
    """
    try:
        stock = yf.Ticker(ticker)

        # 获取历史数据
        if start and end:
            hist = stock.history(start=start, end=end, interval=interval)
        else:
            hist = stock.history(period=period, interval=interval)

        if hist.empty:
            print(f"❌ 未找到股票 {ticker} 的数据", file=sys.stderr)
            return None

        return hist

    except Exception as e:
        print(f"❌ 获取数据失败: {str(e)}", file=sys.stderr)
        return None


def get_stock_info(ticker):
    """
    获取股票基本信息

    Args:
        ticker: 股票代码

    Returns:
        dict: 股票信息
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # 提取关键信息
        key_info = {
            "股票代码": ticker,
            "公司名称": info.get("longName", "N/A"),
            "行业": info.get("industry", "N/A"),
            "板块": info.get("sector", "N/A"),
            "当前价格": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
            "货币": info.get("currency", "N/A"),
            "市值": info.get("marketCap", "N/A"),
            "52周最高": info.get("fiftyTwoWeekHigh", "N/A"),
            "52周最低": info.get("fiftyTwoWeekLow", "N/A"),
            "平均成交量": info.get("averageVolume", "N/A"),
            "市盈率(P/E)": info.get("trailingPE", "N/A"),
            "市净率(P/B)": info.get("priceToBook", "N/A"),
            "股息率": info.get("dividendYield", "N/A"),
        }

        return key_info

    except Exception as e:
        print(f"❌ 获取股票信息失败: {str(e)}", file=sys.stderr)
        return None


def format_number(num):
    """格式化数字显示"""
    if isinstance(num, (int, float)):
        if abs(num) >= 1_000_000_000:
            return f"{num / 1_000_000_000:.2f}B"
        elif abs(num) >= 1_000_000:
            return f"{num / 1_000_000:.2f}M"
        elif abs(num) >= 1_000:
            return f"{num / 1_000:.2f}K"
        else:
            return f"{num:.2f}"
    return num


def main():
    parser = argparse.ArgumentParser(description="获取股票历史数据和基本信息")
    parser.add_argument(
        "--ticker", required=True, help="股票代码（例如: AAPL, 0700.HK, 000001.SS）"
    )
    parser.add_argument("--period", default="1mo", help="时间周期（默认: 1mo）")
    parser.add_argument("--interval", default="1d", help="数据间隔（默认: 1d）")
    parser.add_argument("--start", help="开始日期 (YYYY-MM-DD)")
    parser.add_argument("--end", help="结束日期 (YYYY-MM-DD)")
    parser.add_argument("--output", help="输出文件路径（CSV 格式）")
    parser.add_argument("--info-only", action="store_true", help="仅显示股票基本信息")
    parser.add_argument("--no-info", action="store_true", help="不显示股票基本信息")

    args = parser.parse_args()

    print(f"\n📊 获取股票数据: {args.ticker}")
    print("=" * 60)

    # 获取并显示股票基本信息
    if not args.no_info:
        print("\n📋 股票基本信息:")
        info = get_stock_info(args.ticker)
        if info:
            for key, value in info.items():
                if key == "市值" and isinstance(value, (int, float)):
                    print(f"   {key}: {format_number(value)}")
                elif key == "股息率" and isinstance(value, (int, float)):
                    print(f"   {key}: {value * 100:.2f}%")
                else:
                    print(f"   {key}: {value}")

    if args.info_only:
        return

    # 获取历史数据
    print(f"\n📈 历史数据 (周期: {args.period}, 间隔: {args.interval}):")
    hist = get_stock_data(
        args.ticker,
        period=args.period,
        interval=args.interval,
        start=args.start,
        end=args.end,
    )

    if hist is not None:
        # 显示数据摘要
        print(f"\n数据点数量: {len(hist)}")
        print(f"日期范围: {hist.index[0]} 到 {hist.index[-1]}")

        # 显示最近的数据
        print("\n最近 10 条记录:")
        print(hist.tail(10).to_string())

        # 显示统计信息
        print("\n统计信息:")
        print(hist.describe().to_string())

        # 保存到文件
        if args.output:
            hist.to_csv(args.output)
            print(f"\n✅ 数据已保存到: {args.output}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
