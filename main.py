"""
金融分析多 Agent 系统 - 主程序
使用 Agno 框架构建的综合金融分析系统
"""

from agents.financial_analyst_team import create_financial_analyst_team


def interactive_mode():
    """交互模式"""
    from uuid import uuid4

    print("🚀 金融分析多 Agent 系统 - 交互模式")
    print("=" * 60)
    print()

    # 创建金融分析团队
    print("📊 正在初始化金融分析师团队...")
    team = create_financial_analyst_team()
    print("✅ 团队初始化完成")
    print()

    # 为本次对话创建唯一的 session_id，实现多轮对话
    session_id = str(uuid4())
    print(f"📝 会话 ID: {session_id[:8]}...")
    print()

    print("💡 使用提示：")
    print("  - 输入你的金融分析问题（例如：分析特斯拉的投资价值）")
    print("  - 可以进行多轮对话（例如：追问 '它的估值如何？'）")
    print("  - 输入 'quit' 或 'exit' 退出")
    print("  - 输入 'help' 查看更多帮助")
    print()

    while True:
        try:
            user_input = input("👤 你的问题: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n👋 再见！")
                break

            if user_input.lower() == "help":
                print("\n📖 帮助信息：")
                print("  支持的分析类型：")
                print("    - 个股综合分析：例如 '分析苹果公司(AAPL)的投资价值'")
                print("    - 基本面分析：例如 '特斯拉的财务状况如何？'")
                print("    - 技术分析：例如 'NVDA的技术面现在怎么样？'")
                print("    - 宏观分析：例如 '当前美国经济形势如何？'")
                print("    - 行业分析：例如 '电动车行业的前景如何？'")
                print("  多轮对话示例：")
                print("    第1轮: '分析苹果公司'")
                print("    第2轮: '它的财务状况如何？' (会记住之前说的是苹果)")
                print("    第3轮: '和微软比呢？' (会结合之前的上下文)")
                print()
                continue

            print("\n🤔 正在分析，请稍候...")
            print("-" * 60)

            # 运行分析（流式输出），使用固定的 session_id 实现多轮对话
            team.print_response(user_input, stream=True, session_id=session_id)

            print()
            print("-" * 60)
            print()

        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {str(e)}")
            print("请重试或输入 'quit' 退出")
            print()


if __name__ == "__main__":
    interactive_mode()
