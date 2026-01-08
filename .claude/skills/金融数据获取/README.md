# 金融数据获取 Skill

基于 yfinance 的金融数据获取工具集。

## 快速开始

### 1. 环境设置（必须先执行）

```bash
cd /Users/huiming.yao/workspace/fxxkcompany/.claude/skills/金融数据获取
bash setup.sh
```

### 2. 使用示例

#### 获取股票历史数据

```bash
# 获取苹果公司最近1年的数据
python get_stock_data.py --ticker AAPL --period 1y

# 获取特斯拉最近6个月的数据并保存到文件
python get_stock_data.py --ticker TSLA --period 6mo --output tesla.csv

# 仅查看股票基本信息
python get_stock_data.py --ticker MSFT --info-only
```

#### 获取财务数据

```bash
# 获取利润表（季度）
python get_financial_data.py --ticker AAPL --statement income

# 获取资产负债表（年度）
python get_financial_data.py --ticker AAPL --statement balance --annual

# 获取所有财务报表
python get_financial_data.py --ticker AAPL --statement all --metrics
```

#### 获取市场信息

```bash
# 查看股票实时信息
python get_market_info.py --ticker AAPL

# 查看详细信息
python get_market_info.py --ticker AAPL --info

# 查看市场指数
python get_market_info.py --ticker ^GSPC

# 列出常用市场指数
python get_market_info.py --list-indices
```

#### 技术分析

```bash
# 对股票进行技术分析
python analyze_stock.py --ticker AAPL --period 6mo

# 仅查看交易信号
python analyze_stock.py --ticker AAPL --signals-only

# 指定要计算的指标
python analyze_stock.py --ticker AAPL --indicators SMA RSI MACD --output analysis.csv
```

## 股票代码格式

- **美股**: 直接使用代码，如 `AAPL`, `MSFT`, `GOOGL`
- **港股**: 代码 + `.HK`，如 `0700.HK`, `9988.HK`
- **A股**: 代码 + 市场后缀
  - 上海: `.SS`，如 `600519.SS`
  - 深圳: `.SZ`，如 `000001.SZ`
- **市场指数**:
  - S&P 500: `^GSPC`
  - 纳斯达克: `^IXIC`
  - 道琼斯: `^DJI`
  - 恒生指数: `^HSI`
  - 上证指数: `000001.SS`

## 工具说明

| 脚本                    | 功能         | 主要参数                         |
| ----------------------- | ------------ | -------------------------------- |
| `setup.sh`              | 环境设置     | 无                               |
| `get_stock_data.py`     | 获取历史价格 | --ticker, --period, --interval   |
| `get_financial_data.py` | 获取财务报表 | --ticker, --statement, --annual  |
| `get_market_info.py`    | 获取实时行情 | --ticker, --info                 |
| `analyze_stock.py`      | 技术分析     | --ticker, --period, --indicators |

## 技术指标说明

- **SMA**: 简单移动平均线（20/50/200日）
- **EMA**: 指数移动平均线（12/26日）
- **RSI**: 相对强弱指标（超买>70，超卖<30）
- **MACD**: 平滑异同移动平均线（金叉/死叉）
- **BB**: 布林带（上轨/中轨/下轨）
- **ATR**: 平均真实范围（波动性指标）

## 注意事项

1. ⚠️ 数据来源于 Yahoo Finance，可能存在延迟
2. ⚠️ 仅供学习和研究使用，不构成投资建议
3. ⚠️ 每次使用前确保先运行 `setup.sh` 设置环境
4. ⚠️ 部分市场的数据可能不完整或不可用
