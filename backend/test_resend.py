#!/usr/bin/env python3
"""
Resend邮件服务测试脚本
直接测试邮件发送功能，无需启动完整的API服务
"""

import asyncio
import os
import sys

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.services.email_service import EmailService


async def test_resend_integration():
    """测试Resend邮件集成"""

    print("🧪 开始测试Resend邮件集成...")
    print(f"📧 使用API Key: {settings.RESEND_API_KEY[:10]}...")
    print(f"📤 发件地址: {settings.EMAIL_FROM_ADDRESS}")
    print(f"👤 发件人: {settings.EMAIL_FROM_NAME}")
    print()

    # 获取测试邮箱地址
    test_email = input("请输入您的测试邮箱地址: ").strip()

    if not test_email or "@" not in test_email:
        print("❌ 请输入有效的邮箱地址")
        return

    # 初始化邮件服务
    email_service = EmailService()

    # 检查配置
    if not email_service.is_configured:
        print("❌ 邮件服务配置不完整")
        return

    print(f"📨 正在向 {test_email} 发送测试邮件...")

    try:
        # 发送测试邮件
        success = await email_service.send_test_email(test_email)

        if success:
            print("✅ 测试邮件发送成功！")
            print("📬 请检查您的邮箱收件箱")
            print("📝 如果没有收到，请检查垃圾邮件文件夹")
            print()
            print("🎉 Resend集成测试通过！")
        else:
            print("❌ 测试邮件发送失败")
            print("🔧 请检查API Key和网络连接")

    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        print("🔧 请检查配置和依赖")


def test_email_templates():
    """测试邮件模板"""
    print("\n🎨 测试邮件模板...")

    email_service = EmailService()

    # 测试验证邮件模板
    verification_template = email_service._get_verification_email_template(
        "测试用户", "http://localhost:3000/verify-email?token=test123"
    )

    # 测试重置邮件模板
    reset_template = email_service._get_password_reset_email_template(
        "测试用户", "http://localhost:3000/reset-password?token=test123"
    )

    # 测试欢迎邮件模板
    welcome_template = email_service._get_welcome_email_template("测试用户")

    print("✅ 验证邮件模板生成成功")
    print("✅ 重置密码邮件模板生成成功")
    print("✅ 欢迎邮件模板生成成功")
    print("🎨 所有邮件模板测试通过")


async def main():
    """主测试函数"""
    print("=" * 50)
    print("🚀 LiVin Matrix - Resend邮件服务测试")
    print("=" * 50)

    # 测试邮件模板
    test_email_templates()

    # 测试实际邮件发送
    await test_resend_integration()

    print("\n" + "=" * 50)
    print("🏁 测试完成")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
