#!/usr/bin/env python3
"""
调试Resend API问题
"""

import resend


def debug_resend():
    """调试Resend API"""

    api_key = "re_Ax8gF7Ds_FjVx8o5bDfzUfVdeFmotCp1z"
    test_email = "s9ting.li@gmail.com"

    print("🔍 调试Resend API...")
    print(f"🔑 API Key: {api_key}")
    print(f"📧 测试邮箱: {test_email}")
    print()

    # 设置API Key
    resend.api_key = api_key

    try:
        print("📨 尝试发送简单邮件...")

        # 发送最简单的邮件
        response = resend.Emails.send(
            {
                "from": "LiVin Matrix <noreply@resend.dev>",
                "to": [test_email],
                "subject": "测试邮件",
                "html": "<h1>Hello from LiVin Matrix!</h1><p>这是一封测试邮件。</p>",
            }
        )

        print(f"✅ 发送成功！响应: {response}")

    except Exception as e:
        print(f"❌ 发送失败:")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误信息: {str(e)}")

        # 尝试获取更多错误信息
        if hasattr(e, "response"):
            print(f"   HTTP响应: {e.response}")
        if hasattr(e, "status_code"):
            print(f"   状态码: {e.status_code}")
        if hasattr(e, "message"):
            print(f"   详细消息: {e.message}")

        # 检查API Key格式
        if api_key.startswith("re_"):
            print("✅ API Key格式看起来正确")
        else:
            print("❌ API Key格式可能有问题")

        # 检查邮箱格式
        if "@" in test_email and "." in test_email:
            print("✅ 邮箱格式看起来正确")
        else:
            print("❌ 邮箱格式可能有问题")


if __name__ == "__main__":
    debug_resend()
