"""
邮件发送服务 - 基于Resend HTTP API
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

try:
    import resend
except ImportError:
    resend = None

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """邮件发送服务类 - 使用Resend HTTP API"""

    def __init__(self):
        """初始化邮件服务"""
        self.is_configured = self._check_configuration()

        if self.is_configured and resend:
            resend.api_key = settings.RESEND_API_KEY

    def _check_configuration(self) -> bool:
        """检查邮件服务配置是否完整"""
        required_settings = [
            "RESEND_API_KEY",
            "EMAIL_FROM_ADDRESS",
            "EMAIL_FROM_NAME",
        ]

        for setting in required_settings:
            if not hasattr(settings, setting) or not getattr(settings, setting):
                logger.warning(f"邮件服务配置缺失: {setting}")
                return False

        if not resend:
            logger.warning("Resend SDK未安装，邮件功能不可用")
            return False

        return True

    async def send_verification_email(
        self,
        to_email: str,
        verification_token: str,
        user_name: Optional[str] = None,
    ) -> bool:
        """
        发送邮箱验证邮件

        Args:
            to_email: 收件人邮箱
            verification_token: 验证令牌
            user_name: 用户名（可选）

        Returns:
            发送是否成功
        """
        if not self.is_configured:
            logger.error("邮件服务未配置，无法发送验证邮件")
            return False

        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        display_name = user_name or to_email.split("@")[0]

        subject = "验证您的LiVin Matrix账户"
        html_content = self._get_verification_email_template(display_name, verification_url)

        return await self._send_email(to_email=to_email, subject=subject, html_content=html_content)

    async def send_password_reset_email(self, to_email: str, reset_token: str, user_name: Optional[str] = None) -> bool:
        """
        发送密码重置邮件

        Args:
            to_email: 收件人邮箱
            reset_token: 重置令牌
            user_name: 用户名（可选）

        Returns:
            发送是否成功
        """
        if not self.is_configured:
            logger.error("邮件服务未配置，无法发送重置邮件")
            return False

        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        display_name = user_name or to_email.split("@")[0]

        subject = "重置您的LiVin Matrix密码"
        html_content = self._get_password_reset_email_template(display_name, reset_url)

        return await self._send_email(to_email=to_email, subject=subject, html_content=html_content)

    async def send_welcome_email(self, to_email: str, user_name: Optional[str] = None) -> bool:
        """
        发送欢迎邮件

        Args:
            to_email: 收件人邮箱
            user_name: 用户名（可选）

        Returns:
            发送是否成功
        """
        if not self.is_configured:
            logger.error("邮件服务未配置，无法发送欢迎邮件")
            return False

        display_name = user_name or to_email.split("@")[0]

        subject = "欢迎加入LiVin Matrix!"
        html_content = self._get_welcome_email_template(display_name)

        return await self._send_email(to_email=to_email, subject=subject, html_content=html_content)

    async def send_test_email(self, to_email: str) -> bool:
        """
        发送测试邮件

        Args:
            to_email: 收件人邮箱

        Returns:
            发送是否成功
        """
        if not self.is_configured:
            logger.error("邮件服务未配置，无法发送测试邮件")
            return False

        subject = "LiVin Matrix - 邮件服务测试"
        html_content = self._get_test_email_template()

        return await self._send_email(to_email=to_email, subject=subject, html_content=html_content)

    async def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        发送邮件的通用方法

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML内容

        Returns:
            发送是否成功
        """
        try:
            # 使用Resend API发送邮件
            email_response = resend.Emails.send(
                {
                    "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM_ADDRESS}>",
                    "to": [to_email],
                    "subject": subject,
                    "html": html_content,
                }
            )

            if email_response and (
                hasattr(email_response, "id") or (isinstance(email_response, dict) and "id" in email_response)
            ):
                response_id = email_response.id if hasattr(email_response, "id") else email_response.get("id")
                logger.info(f"邮件发送成功: {response_id} -> {to_email}")
                return True
            else:
                logger.error(f"邮件发送失败，无响应ID -> {to_email}")
                return False

        except Exception as e:
            logger.error(f"邮件发送异常 -> {to_email}: {str(e)}")
            return False

    def _get_verification_email_template(self, user_name: str, verification_url: str) -> str:
        """获取邮箱验证邮件模板"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>验证您的邮箱</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #2563eb; margin-bottom: 10px;">LiVin Matrix</h1>
                <p style="color: #666; margin: 0;">个人生活管理平台</p>
            </div>

            <div style="background-color: #f8fafc; padding: 30px; border-radius: 8px; margin-bottom: 20px;">
                <h2 style="color: #1e293b; margin-top: 0;">您好，{user_name}！</h2>
                <p style="margin-bottom: 25px;">感谢您注册LiVin Matrix账户。请点击下面的按钮验证您的邮箱地址：</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}"
                       style="background-color: #2563eb; color: white; padding: 12px 30px;
                              text-decoration: none; border-radius: 6px; display: inline-block;
                              font-weight: bold; font-size: 16px;">
                        验证邮箱地址
                    </a>
                </div>

                <p style="margin-top: 25px; color: #666; font-size: 14px;">
                    如果按钮无法点击，请复制以下链接到浏览器地址栏：<br>
                    <a href="{verification_url}" style="color: #2563eb; word-break: break-all;">{verification_url}</a>
                </p>
            </div>

            <div style="border-top: 1px solid #e2e8f0; padding-top: 20px; color: #666; font-size: 12px;">
                <p><strong>重要提醒：</strong></p>
                <ul style="margin: 10px 0; padding-left: 20px;">
                    <li>此验证链接将在24小时后过期</li>
                    <li>如果您没有注册LiVin Matrix账户，请忽略此邮件</li>
                    <li>请勿回复此邮件，该邮箱不接收回复</li>
                </ul>

                <p style="margin-top: 20px; text-align: center;">
                    © 2025 LiVin Matrix. 保留所有权利。
                </p>
            </div>
        </body>
        </html>
        """

    def _get_password_reset_email_template(self, user_name: str, reset_url: str) -> str:
        """获取密码重置邮件模板"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>重置您的密码</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #dc2626; margin-bottom: 10px;">LiVin Matrix</h1>
                <p style="color: #666; margin: 0;">密码重置请求</p>
            </div>

            <div style="background-color: #fef2f2; border: 1px solid #fecaca; padding: 30px; border-radius: 8px; margin-bottom: 20px;">
                <h2 style="color: #991b1b; margin-top: 0;">您好，{user_name}！</h2>
                <p style="margin-bottom: 25px;">我们收到了您的密码重置请求。点击下面的按钮设置新密码：</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}"
                       style="background-color: #dc2626; color: white; padding: 12px 30px;
                              text-decoration: none; border-radius: 6px; display: inline-block;
                              font-weight: bold; font-size: 16px;">
                        重置密码
                    </a>
                </div>

                <p style="margin-top: 25px; color: #666; font-size: 14px;">
                    如果按钮无法点击，请复制以下链接到浏览器地址栏：<br>
                    <a href="{reset_url}" style="color: #dc2626; word-break: break-all;">{reset_url}</a>
                </p>
            </div>

            <div style="border-top: 1px solid #e2e8f0; padding-top: 20px; color: #666; font-size: 12px;">
                <p><strong>安全提醒：</strong></p>
                <ul style="margin: 10px 0; padding-left: 20px;">
                    <li>此重置链接将在1小时后过期</li>
                    <li>如果您没有请求重置密码，请忽略此邮件</li>
                    <li>为了账户安全，请使用强密码</li>
                    <li>请勿与他人分享此链接</li>
                </ul>

                <p style="margin-top: 20px; text-align: center;">
                    © 2025 LiVin Matrix. 保留所有权利。
                </p>
            </div>
        </body>
        </html>
        """

    def _get_welcome_email_template(self, user_name: str) -> str:
        """获取欢迎邮件模板"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>欢迎加入LiVin Matrix</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #059669; margin-bottom: 10px;">🎉 欢迎加入LiVin Matrix！</h1>
                <p style="color: #666; margin: 0;">您的个人生活管理之旅从这里开始</p>
            </div>

            <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 30px; border-radius: 8px; margin-bottom: 20px;">
                <h2 style="color: #065f46; margin-top: 0;">您好，{user_name}！</h2>
                <p style="margin-bottom: 20px;">恭喜您成功注册LiVin Matrix账户！我们很高兴您选择我们的平台来管理您的日常生活。</p>

                <h3 style="color: #065f46; margin-top: 25px;">接下来您可以：</h3>
                <ul style="margin: 15px 0; padding-left: 20px;">
                    <li style="margin-bottom: 8px;">📝 记录每日生活点滴</li>
                    <li style="margin-bottom: 8px;">📊 查看生活数据分析</li>
                    <li style="margin-bottom: 8px;">🎯 设定和追踪个人目标</li>
                    <li style="margin-bottom: 8px;">💡 获得个性化生活建议</li>
                </ul>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/login"
                       style="background-color: #059669; color: white; padding: 12px 30px;
                              text-decoration: none; border-radius: 6px; display: inline-block;
                              font-weight: bold; font-size: 16px;">
                        开始使用
                    </a>
                </div>
            </div>

            <div style="border-top: 1px solid #e2e8f0; padding-top: 20px; color: #666; font-size: 12px;">
                <p style="margin-bottom: 15px;">如果您在使用过程中遇到任何问题，欢迎联系我们的支持团队。</p>

                <p style="margin-top: 20px; text-align: center;">
                    © 2025 LiVin Matrix. 保留所有权利。
                </p>
            </div>
        </body>
        </html>
        """

    def _get_test_email_template(self) -> str:
        """获取测试邮件模板"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>邮件服务测试</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #6366f1; margin-bottom: 10px;">LiVin Matrix</h1>
                <p style="color: #666; margin: 0;">邮件服务测试</p>
            </div>

            <div style="background-color: #f1f5f9; padding: 30px; border-radius: 8px; margin-bottom: 20px;">
                <h2 style="color: #334155; margin-top: 0;">🧪 邮件服务测试</h2>
                <p style="margin-bottom: 20px;">如果您收到此邮件，说明Resend邮件服务配置成功！</p>

                <div style="background-color: #fff; padding: 20px; border-radius: 6px; border-left: 4px solid #6366f1;">
                    <h3 style="color: #4338ca; margin-top: 0;">测试信息：</h3>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li><strong>发送时间：</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</li>
                        <li><strong>邮件服务：</strong> Resend HTTP API</li>
                        <li><strong>状态：</strong> ✅ 工作正常</li>
                    </ul>
                </div>
            </div>

            <div style="border-top: 1px solid #e2e8f0; padding-top: 20px; color: #666; font-size: 12px; text-align: center;">
                <p>此邮件由LiVin Matrix系统自动发送，请勿回复。</p>
                <p style="margin-top: 10px;">© 2025 LiVin Matrix. 保留所有权利。</p>
            </div>
        </body>
        </html>
        """
