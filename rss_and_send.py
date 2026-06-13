#!/usr/bin/env python3
"""
组合脚本：生成EPUB并自动发送到Kindle（Secrets版本）
"""

import sys
import argparse
import os

from main import main as generate_epub
from send_to_kindle import send_to_kindle, get_latest_epub


def load_email_config_from_secrets():
    """从环境变量读取 GitHub Secrets"""
    config = {
        "smtp_server": os.getenv("SMTP_SERVER"),
        "smtp_port": os.getenv("SMTP_PORT"),
        "sender_email": os.getenv("SENDER_EMAIL"),
        "sender_password": os.getenv("SENDER_PASSWORD"),
        "kindle_email": os.getenv("KINDLE_EMAIL"),
        "subject": f"RSS Feed - {os.popen('date +%Y-%m-%d').read().strip()}",
        "body": f"RSS 内容 - {os.popen('date +%Y-%m-%d').read().strip()}"
    }

    # 基本校验
    if not all([config["smtp_server"], config["sender_email"], config["sender_password"], config["kindle_email"]]):
        return None

    return config


def main():
    parser = argparse.ArgumentParser(description='生成RSS EPUB并发送到Kindle')
    parser.add_argument('--no-send', action='store_true', help='仅生成EPUB，不发送邮件')
    parser.add_argument('--send-only', action='store_true', help='仅发送最新EPUB，不生成新的')
    args = parser.parse_args()

    # =========================
    # 1. 生成 EPUB
    # =========================
    if not args.send_only:
        print("=" * 50)
        print("📖 开始生成EPUB...")
        print("=" * 50)
        try:
            generate_epub()
            print("✅ EPUB生成成功！")
        except Exception as e:
            print(f"❌ EPUB生成失败: {e}")
            return 1

    # =========================
    # 2. 发送 Kindle
    # =========================
    if not args.no_send:

        print("\n" + "=" * 50)
        print("📧 准备发送到Kindle...")
        print("=" * 50)

        config = load_email_config_from_secrets()
        if not config:
            print("❌ 未检测到 GitHub Secrets 邮件配置")
            print("   请检查 Actions 中是否正确设置 SMTP / Kindle secrets")
            return 0

        epub_file = get_latest_epub()
        if not epub_file:
            print("❌ 没有找到EPUB文件")
            return 1

        if send_to_kindle(epub_file, config):
            print("\n" + "=" * 50)
            print("🎉 完成！EPUB已发送到Kindle")
            print("=" * 50)
            return 0
        else:
            print("⚠️ EPUB生成成功但发送失败")
            return 1

    print("\n" + "=" * 50)
    print("✅ EPUB生成完成（未发送邮件）")
    print("=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(main())
