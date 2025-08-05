#!/usr/bin/env python3
"""
直接测试Resend API，不依赖项目配置
"""

import asyncio


async def test_resend_direct():
    """直接测试Resend API"""

    try:
        import resend
    except ImportError:
        print("❌ Resend SDK未安装")
        print("💡 请运行: pip3 install resend==0.8.0")
        return False

    # 直接设置API Key
    api_key = "re_Ax8gF7Ds_FjVx8o5bDfzUfVdeFmotCp1z"
    test_email = "s9ting.li@gmail.com"
    from_email = "noreply@resend.dev"
    from_name = "LiVin Matrix Team"

    print("🧪 直接测试Resend API...")
    print(f"🔑 API Key: {api_key[:10]}...")
    print(f"📧 目标邮箱: {test_email}")
    print(f"📤 发件人: {from_name} <{from_email}>")
    print()

    # 设置API Key
    resend.api_key = api_key

    try:
        print("📨 正在发送测试邮件...")

        # 构建邮件内容
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>LiVin Matrix 邮件测试</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #6366f1;">🎉 LiVin Matrix</h1>
                <p style="color: #666;">邮件服务测试成功！</p>
            </div>
            
            <div style="background-color: #f1f5f9; padding: 30px; border-radius: 8px;">
                <h2 style="color: #334155; margin-top: 0;">📧 测试邮件</h2>
                <p>如果您收到此邮件，说明Resend邮件服务配置成功！</p>
                
                <div style="background-color: #fff; padding: 20px; border-radius: 6px; margin: 20px 0;">
                    <h3 style="color: #4338ca; margin-top: 0;">✅ 测试信息：</h3>
                    <ul>
                        <li><strong>发送时间：</strong> 2025-08-04 测试</li>
                        <li><strong>邮件服务：</strong> Resend HTTP API</li>
                        <li><strong>状态：</strong> 工作正常</li>
                        <li><strong>API Key：</strong> {api_key[:10]}...</li>
                    </ul>
                </div>
                
                <p style="color: #059669; font-weight: bold;">🎊 恭喜！邮箱登录功能的邮件发送服务已准备就绪！</p>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #666; font-size: 12px; text-align: center;">
                <p>此邮件由 LiVin Matrix 系统自动发送，请勿回复。</p>
                <p>© 2025 LiVin Matrix. 保留所有权利。</p>
            </div>
        </body>
        </html>
        """

        # 发送邮件
        email_response = resend.Emails.send(
            {
                "from": f"{from_name} <{from_email}>",
                "to": [test_email],
                "subject": "🧪 LiVin Matrix - 邮件服务测试成功！",
                "html": html_content,
            }
        )

        if email_response and hasattr(email_response, "id"):
            print(f"✅ 邮件发送成功！")
            print(f"📬 邮件ID: {email_response.id}")
            print(f"📧 目标地址: {test_email}")
            print()
            print("🎉 请检查您的邮箱收件箱！")
            print("📝 如果没有收到，请检查垃圾邮件文件夹")
            print("⏰ 邮件通常在1-2分钟内到达")
            print()
            print("🔗 您也可以访问 Resend 控制台查看详细状态:")
            print("   https://resend.com/logs")
            return True
        else:
            print("❌ 邮件发送失败，无响应ID")
            return False

    except Exception as e:
        print(f"❌ 邮件发送过程中发生错误:")
        print(f"   错误信息: {str(e)}")
        print(f"   错误类型: {type(e).__name__}")

        if "401" in str(e) or "unauthorized" in str(e).lower():
            print("🔧 可能的解决方案:")
            print("   - 检查API Key是否正确")
            print("   - 确认API Key是否已激活")
            print("   - 验证Resend账户状态")
        elif "403" in str(e) or "forbidden" in str(e).lower():
            print("🔧 可能的解决方案:")
            print("   - 检查发件域名是否已验证")
            print("   - 确认是否超出发送配额")
        else:
            print("🔧 可能的解决方案:")
            print("   - 检查网络连接")
            print("   - 确认目标邮箱地址格式正确")

        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 LiVin Matrix - 直接Resend API测试")
    print("=" * 60)

    success = asyncio.run(test_resend_direct())

    print("\n" + "=" * 60)
    if success:
        print("🎊 测试成功！Resend邮件集成工作正常")
        print("✅ 邮箱登录功能的邮件服务已准备就绪")
    else:
        print("❌ 测试失败，需要检查配置")
    print("=" * 60)
