#!/usr/bin/env python3
"""
简化的Resend邮件测试
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.email_service import EmailService


async def test_email_send(test_email: str):
    """测试发送邮件到指定地址"""

    print("🧪 开始测试Resend邮件集成...")
    print(f"📨 目标邮箱: {test_email}")

    # 初始化邮件服务
    email_service = EmailService()

    # 检查配置
    if not email_service.is_configured:
        print("❌ 邮件服务配置不完整")
        print("🔧 请检查以下配置项:")
        print("   - RESEND_API_KEY")
        print("   - EMAIL_FROM_ADDRESS")
        print("   - EMAIL_FROM_NAME")
        return False

    print("✅ 邮件服务配置正常")

    try:
        # 发送测试邮件
        print("📤 正在发送测试邮件...")
        success = await email_service.send_test_email(test_email)

        if success:
            print("✅ 测试邮件发送成功！")
            print("📬 请检查邮箱收件箱和垃圾邮件文件夹")
            print("🎉 Resend集成测试通过！")
            return True
        else:
            print("❌ 测试邮件发送失败")
            print("🔧 可能的原因:")
            print("   - API Key无效")
            print("   - 网络连接问题")
            print("   - 目标邮箱地址无效")
            return False

    except Exception as e:
        print(f"❌ 发送过程中发生错误: {str(e)}")
        return False


if __name__ == "__main__":
    # 您可以在这里修改测试邮箱地址
    TEST_EMAIL = "s9ting.li@gmail.com"  # 使用真实邮箱进行测试

    print("=" * 50)
    print("🚀 LiVin Matrix - 简化邮件测试")
    print("=" * 50)
    print(f"⚠️  请将 TEST_EMAIL 修改为您的真实邮箱地址")
    print(f"📧 当前测试邮箱: {TEST_EMAIL}")
    print("=" * 50)

    if TEST_EMAIL == "your-email@example.com":
        print("❌ 请先修改脚本中的 TEST_EMAIL 变量为您的真实邮箱地址")
        exit(1)

    result = asyncio.run(test_email_send(TEST_EMAIL))

    print("\n" + "=" * 50)
    if result:
        print("🎉 测试成功完成")
    else:
        print("❌ 测试失败")
    print("=" * 50)
