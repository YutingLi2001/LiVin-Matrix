"""
GitHub OAuth服务
"""

from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import generate_state_parameter


class GitHubOAuthService:
    """GitHub OAuth认证服务"""

    GITHUB_OAUTH_URL = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
    GITHUB_USER_URL = "https://api.github.com/user"
    GITHUB_USER_EMAILS_URL = "https://api.github.com/user/emails"

    def get_auth_url(self, state: Optional[str] = None) -> Dict[str, str]:
        """
        生成GitHub OAuth授权URL

        Returns:
            Dict containing auth_url and state
        """
        if not state:
            state = generate_state_parameter()

        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": settings.GITHUB_REDIRECT_URI,
            "scope": "user:email",
            "state": state,
            "allow_signup": "true",
        }

        auth_url = f"{self.GITHUB_OAUTH_URL}?{urlencode(params)}"

        return {"auth_url": auth_url, "state": state}

    async def exchange_code_for_token(self, code: str) -> str:
        """
        交换授权码获取访问令牌

        Args:
            code: GitHub返回的授权码

        Returns:
            GitHub访问令牌

        Raises:
            HTTPException: 当令牌交换失败时
        """
        try:
            data = {
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GITHUB_REDIRECT_URI,
            }

            headers = {
                "Accept": "application/json",
                "User-Agent": "LiVin-Matrix/1.0",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.GITHUB_TOKEN_URL,
                    data=data,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()

                token_data = response.json()

                if "error" in token_data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"GitHub OAuth错误: {token_data.get('error_description', token_data['error'])}",
                    )

                access_token = token_data.get("access_token")
                if not access_token:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="未能获取GitHub访问令牌",
                    )

                return access_token

        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"GitHub API请求失败: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"令牌交换失败: {str(e)}",
            )

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        通过访问令牌获取GitHub用户信息

        Args:
            access_token: GitHub访问令牌

        Returns:
            用户信息字典

        Raises:
            HTTPException: 当获取用户信息失败时
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "LiVin-Matrix/1.0",
            }

            async with httpx.AsyncClient() as client:
                # 获取用户基本信息
                user_response = await client.get(self.GITHUB_USER_URL, headers=headers, timeout=30.0)
                user_response.raise_for_status()
                user_data = user_response.json()

                # 获取用户邮箱信息
                email_response = await client.get(self.GITHUB_USER_EMAILS_URL, headers=headers, timeout=30.0)
                email_response.raise_for_status()
                emails_data = email_response.json()

                # 查找主要邮箱
                primary_email = None
                for email_info in emails_data:
                    if email_info.get("primary", False) and email_info.get("verified", False):
                        primary_email = email_info["email"]
                        break

                if not primary_email and emails_data:
                    # 如果没有主要邮箱，使用第一个已验证的邮箱
                    for email_info in emails_data:
                        if email_info.get("verified", False):
                            primary_email = email_info["email"]
                            break

                if not primary_email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="无法获取已验证的GitHub邮箱地址",
                    )

                # 构建用户信息
                user_info = {
                    "github_user_id": user_data["id"],
                    "github_username": user_data["login"],
                    "email": primary_email,
                    "name": user_data.get("name"),
                    "avatar_url": user_data.get("avatar_url"),
                    "bio": user_data.get("bio"),
                    "location": user_data.get("location"),
                    "public_repos": user_data.get("public_repos", 0),
                    "followers": user_data.get("followers", 0),
                    "following": user_data.get("following", 0),
                }

                return user_info

        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"GitHub API请求失败: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取用户信息失败: {str(e)}",
            )
