#!/usr/bin/env python3
"""
获取市场信息

使用 yfinance 获取股票或市场指数的实时信息
"""

import argparse
import sys
from datetime import datetime
import yfinance as yf


def get_market_info(ticker, detailed=False):
    """
    获取市场信息

    Args:
        ticker: 股票代码或指数代码
        detailed: 是否显示详细信息

    Returns:
        dict: 市场信息
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info:
            print(f"❌ 未找到 {ticker} 的信息", file=sys.stderr)
            return None

        # 基本信息
        basic_info = {
            "代码": ticker,
            "名称": info.get("longName", info.get("shortName", "N/A")),
            "类型": info.get("quoteType", "N/A"),
            "交易所": info.get("exchange", "N/A"),
            "货币": info.get("currency", "N/A"),
        }

        # 价格信息
        price_info = {
            "当前价格": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
            "前收盘价": info.get("previousClose", "N/A"),
            "开盘价": info.get("open", "N/A"),
            "最高价": info.get("dayHigh", "N/A"),
            "最低价": info.get("dayLow", "N/A"),
            "52周最高": info.get("fiftyTwoWeekHigh", "N/A"),
            "52周最低": info.get("fiftyTwoWeekLow", "N/A"),
        }

        # 计算涨跌
        current = price_info["当前价格"]
        previous = price_info["前收盘价"]
        if (
            isinstance(current, (int, float))
            and isinstance(previous, (int, float))
            and previous != 0
        ):
            change = current - previous
            change_percent = (change / previous) * 100
            price_info["涨跌额"] = f"{change:+.2f}"
            price_info["涨跌幅"] = f"{change_percent:+.2f}%"

        # 交易信息
        trading_info = {
            "成交量": info.get("volume", "N/A"),
            "平均成交量": info.get("averageVolume", "N/A"),
            "市值": info.get("marketCap", "N/A"),
        }

        result = {
            "基本信息": basic_info,
            "价格信息": price_info,
            "交易信息": trading_info,
        }

        # 详细信息（仅股票）
        if detailed and info.get("quoteType") == "EQUITY":
            valuation_info = {
                "市盈率(P/E)": info.get("trailingPE", info.get("forwardPE", "N/A")),
                "市净率(P/B)": info.get("priceToBook", "N/A"),
                "市销率(P/S)": info.get("priceToSalesTrailing12Months", "N/A"),
                "PEG比率": info.get("pegRatio", "N/A"),
                "股息率": info.get("dividendYield", "N/A"),
                "Beta": info.get("beta", "N/A"),
            }

            financial_info = {
                "总收入": info.get("totalRevenue", "N/A"),
                "毛利润": info.get("grossProfits", "N/A"),
                "营业利润": info.get("operatingIncome", "N/A"),
                "净利润": info.get("netIncomeToCommon", "N/A"),
                "每股收益(EPS)": info.get("trailingEps", "N/A"),
                "总资产": info.get("totalAssets", "N/A"),
                "总负债": info.get("totalDebt", "N/A"),
                "股东权益": info.get("totalStockholderEquity", "N/A"),
            }

            result["估值指标"] = valuation_info
            result["财务指标"] = financial_info

        return result

    except Exception as e:
        print(f"❌ 获取市场信息失败: {str(e)}", file=sys.stderr)
        return None


def format_value(value):
    """格式化显示值"""
    if isinstance(value, (int, float)):
        if abs(value) >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        elif abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        elif abs(value) >= 1_000:
            return f"{value / 1_000:.2f}K"
        elif abs(value) < 1 and value != 0:
            return f"{value:.4f}"
        else:
            return f"{value:.2f}"
    return value


def print_market_info(info):
    """打印市场信息"""
    for category, data in info.items():
        print(f"\n{category}:")
        print("-" * 50)
        for key, value in data.items():
            if key == "股息率" and isinstance(value, float):
                print(f"  {key:20}: {value * 100:.2f}%")
            elif isinstance(value, (int, float)) and key not in ["涨跌额", "涨跌幅"]:
                print(f"  {key:20}: {format_value(value)}")
            else:
                print(f"  {key:20}: {value}")


def get_popular_indices():
    """返回常用市场指数列表"""
    return {
        "美国市场": {
            "^GSPC": "S&P 500",
            "^DJI": "道琼斯工业平均指数",
            "^IXIC": "纳斯达克综合指数",
            "^RUT": "罗素 2000",
        },
        "亚太市场": {
            "^HSI": "恒生指数",
            "000001.SS": "上证指数",
            "399001.SZ": "深证成指",
            "^N225": "日经 225",
        },
        "欧洲市场": {
            "^FTSE": "富时 100",
            "^GDAXI": "DAX",
            "^FCHI": "CAC 40",
        },
    }


def main():
    parser = argparse.ArgumentParser(description="获取市场信息和实时行情")
    parser.add_argument("--ticker", help="股票代码或指数代码（例如: AAPL, ^GSPC）")
    parser.add_argument("--info", action="store_true", help="显示详细信息")
    parser.add_argument("--list-indices", action="store_true", help="列出常用市场指数")

    args = parser.parse_args()

    if args.list_indices:
        print("\n📊 常用市场指数:")
        print("=" * 60)
        indices = get_popular_indices()
        for region, index_dict in indices.items():
            print(f"\n{region}:")
            for code, name in index_dict.items():
                print(f"  {code:15} - {name}")
        print("\n使用示例: python get_market_info.py --ticker ^GSPC")
        return

    if not args.ticker:
        parser.error("请提供 --ticker 参数或使用 --list-indices 查看可用指数")

    print(f"\n📊 市场信息: {args.ticker}")
    print("=" * 60)
    print(f"查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    info = get_market_info(args.ticker, detailed=args.info)

    if info:
        print_market_info(info)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
