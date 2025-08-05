#!/usr/bin/env python3
"""
发送测试邮件到Resend注册邮箱
"""

import json

import requests


def test_email_to_registered():
    """发送邮件到Resend注册的邮箱地址"""

    api_key = "re_Ax8gF7Ds_FjVx8o5bDfzUfVdeFmotCp1z"
    # 根据错误信息，这是您的Resend注册邮箱
    registered_email = "livinfoundry@gmail.com"

    print("🔍 发送测试邮件到Resend注册邮箱...")
    print(f"🔑 API Key: {api_key[:10]}...")
    print(f"📧 注册邮箱: {registered_email}")
    print(f"📝 注意: 免费Resend账户只能发送到注册邮箱")
    print()

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {
        "from": "LiVin Matrix <noreply@resend.dev>",
        "to": [registered_email],
        "subject": "🎉 LiVin Matrix - 邮件服务测试成功！",
        "html": """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>LiVin Matrix 邮件测试</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #059669;">🎉 LiVin Matrix</h1>
                <p style="color: #666;">邮件服务测试成功！</p>
            </div>
            
            <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 30px; border-radius: 8px;">
                <h2 style="color: #065f46; margin-top: 0;">✅ 邮件服务配置成功！</h2>
                <p>恭喜！如果您收到此邮件，说明LiVin Matrix的邮件服务已经正确配置。</p>
                
                <div style="background-color: #fff; padding: 20px; border-radius: 6px; margin: 20px 0;">
                    <h3 style="color: #059669; margin-top: 0;">📊 测试详情：</h3>
                    <ul>
                        <li><strong>邮件服务：</strong> Resend HTTP API</li>
                        <li><strong>API Key：</strong> re_Ax8gF7D... (已配置)</li>
                        <li><strong>发件人：</strong> LiVin Matrix Team</li>
                        <li><strong>测试时间：</strong> 2025-08-04</li>
                        <li><strong>状态：</strong> ✅ 正常工作</li>
                    </ul>
                </div>
                
                <div style="background-color: #fef3c7; border: 1px solid #f59e0b; padding: 15px; border-radius: 6px; margin: 20px 0;">
                    <h4 style="color: #92400e; margin-top: 0;">📝 重要提醒：</h4>
                    <p style="margin: 0; color: #92400e;">
                        当前使用的是Resend免费测试模式，只能发送邮件到注册邮箱。
                        如需发送到其他邮箱地址，请在 <a href="https://resend.com/domains" style="color: #059669;">resend.com/domains</a> 验证您的域名。
                    </p>
                </div>
                
                <h3 style="color: #065f46;">🚀 接下来的步骤：</h3>
                <ol>
                    <li>✅ 邮件服务测试完成</li>
                    <li>🔄 继续开发前端登录页面</li>
                    <li>🧪 进行完整的用户注册流程测试</li>
                    <li>🌐 （可选）验证自定义域名以发送到任意邮箱</li>
                </ol>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #666; font-size: 12px; text-align: center;">
                <p>此邮件由 LiVin Matrix 邮箱认证系统自动发送</p>
                <p>© 2025 LiVin Matrix. 保留所有权利。</p>
            </div>
        </body>
        </html>
        """,
    }

    try:
        print("📨 正在发送测试邮件...")
        response = requests.post(
            "https://api.resend.com/emails", headers=headers, json=data, timeout=10
        )

        print(f"📊 HTTP状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ 邮件发送成功！")
            print(f"📬 邮件ID: {result.get('id', '未知')}")
            print(f"📧 目标邮箱: {registered_email}")
            print()
            print("🎉 请检查您的邮箱收件箱！")
            print("📝 如果没有收到，请检查垃圾邮件文件夹")
            print("⏰ 邮件通常在1-2分钟内到达")
            print()
            print("🔗 您也可以访问 Resend 控制台查看详细状态:")
            print("   https://resend.com/logs")

            return True
        else:
            print("❌ 邮件发送失败")
            print(f"📋 响应内容: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 发送过程中发生错误: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 LiVin Matrix - Resend注册邮箱测试")
    print("=" * 60)

    success = test_email_to_registered()

    print("\n" + "=" * 60)
    if success:
        print("🎊 测试成功！Resend邮件服务工作正常")
        print("✅ 邮箱登录功能的邮件发送已准备就绪")
        print()
        print("💡 下一步建议:")
        print("   1. 继续前端开发")
        print("   2. 测试完整用户注册流程")
        print("   3. (可选) 在resend.com验证域名以支持任意邮箱")
    else:
        print("❌ 测试失败，需要进一步调试")
    print("=" * 60)
