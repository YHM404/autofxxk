#!/usr/bin/env python3
"""
获取公司财务数据

使用 yfinance 获取公司的财务报表数据
"""

import argparse
import sys
import yfinance as yf
import pandas as pd


def get_financial_statements(ticker, statement_type, annual=False):
    """
    获取财务报表

    Args:
        ticker: 股票代码
        statement_type: 报表类型 ('income', 'balance', 'cashflow')
        annual: 是否获取年度报表（默认为季度报表）

    Returns:
        DataFrame: 财务报表数据
    """
    try:
        stock = yf.Ticker(ticker)

        if statement_type == "income":
            df = stock.financials if annual else stock.quarterly_financials
            title = "利润表 (Income Statement)"
        elif statement_type == "balance":
            df = stock.balance_sheet if annual else stock.quarterly_balance_sheet
            title = "资产负债表 (Balance Sheet)"
        elif statement_type == "cashflow":
            df = stock.cashflow if annual else stock.quarterly_cashflow
            title = "现金流量表 (Cash Flow Statement)"
        else:
            print(f"❌ 无效的报表类型: {statement_type}", file=sys.stderr)
            return None, None

        if df is None or df.empty:
            print(f"❌ 未找到 {ticker} 的财务数据", file=sys.stderr)
            return None, None

        return df, title

    except Exception as e:
        print(f"❌ 获取财务数据失败: {str(e)}", file=sys.stderr)
        return None, None


def format_financial_value(value):
    """格式化财务数值"""
    if pd.isna(value):
        return "N/A"
    if isinstance(value, (int, float)):
        if abs(value) >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        elif abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        elif abs(value) >= 1_000:
            return f"{value / 1_000:.2f}K"
        else:
            return f"{value:.2f}"
    return str(value)


def get_key_metrics(ticker):
    """
    获取关键财务指标

    Args:
        ticker: 股票代码

    Returns:
        dict: 关键指标
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        metrics = {
            "收入 (Revenue)": info.get("totalRevenue", "N/A"),
            "毛利润 (Gross Profit)": info.get("grossProfits", "N/A"),
            "营业利润 (Operating Income)": info.get("operatingIncome", "N/A"),
            "净利润 (Net Income)": info.get("netIncomeToCommon", "N/A"),
            "每股收益 (EPS)": info.get("trailingEps", "N/A"),
            "总资产 (Total Assets)": info.get("totalAssets", "N/A"),
            "总负债 (Total Debt)": info.get("totalDebt", "N/A"),
            "股东权益 (Shareholders Equity)": info.get("totalStockholderEquity", "N/A"),
            "经营现金流 (Operating Cash Flow)": info.get("operatingCashflow", "N/A"),
            "自由现金流 (Free Cash Flow)": info.get("freeCashflow", "N/A"),
            "毛利率 (Gross Margin)": info.get("grossMargins", "N/A"),
            "营业利润率 (Operating Margin)": info.get("operatingMargins", "N/A"),
            "净利率 (Profit Margin)": info.get("profitMargins", "N/A"),
            "资产收益率 (ROA)": info.get("returnOnAssets", "N/A"),
            "股东权益报酬率 (ROE)": info.get("returnOnEquity", "N/A"),
        }

        return metrics

    except Exception as e:
        print(f"❌ 获取关键指标失败: {str(e)}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="获取公司财务报表数据")
    parser.add_argument(
        "--ticker", required=True, help="股票代码（例如: AAPL, 0700.HK）"
    )
    parser.add_argument(
        "--statement",
        required=True,
        choices=["income", "balance", "cashflow", "all"],
        help="报表类型: income(利润表), balance(资产负债表), cashflow(现金流量表), all(全部)",
    )
    parser.add_argument(
        "--annual", action="store_true", help="获取年度报表（默认为季度报表）"
    )
    parser.add_argument("--metrics", action="store_true", help="显示关键财务指标")
    parser.add_argument("--output", help="输出文件路径前缀（CSV 格式）")

    args = parser.parse_args()

    print(f"\n📊 获取财务数据: {args.ticker}")
    print("=" * 80)

    period_type = "年度" if args.annual else "季度"

    # 获取关键指标
    if args.metrics:
        print(f"\n📈 关键财务指标:")
        metrics = get_key_metrics(args.ticker)
        if metrics:
            for key, value in metrics.items():
                if (
                    isinstance(value, float)
                    and "Rate" not in key
                    and "Margin" not in key
                    and "ROA" not in key
                    and "ROE" not in key
                ):
                    print(f"   {key}: {format_financial_value(value)}")
                elif isinstance(value, float) and (
                    "Rate" in key or "Margin" in key or "ROA" in key or "ROE" in key
                ):
                    print(f"   {key}: {value * 100:.2f}%")
                else:
                    print(f"   {key}: {value}")

    # 获取财务报表
    statements = (
        ["income", "balance", "cashflow"]
        if args.statement == "all"
        else [args.statement]
    )

    for stmt in statements:
        df, title = get_financial_statements(args.ticker, stmt, args.annual)

        if df is not None:
            print(f"\n{title} ({period_type}):")
            print("-" * 80)

            # 转置数据框以便更好地显示
            df_display = df.T

            # 显示数据
            print(df_display.to_string())

            # 保存到文件
            if args.output:
                output_file = f"{args.output}_{stmt}_{'annual' if args.annual else 'quarterly'}.csv"
                df.to_csv(output_file)
                print(f"\n✅ 数据已保存到: {output_file}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
