"""ファイル管理モジュール（添付ファイルのダウンロード）"""

import aiohttp
import asyncio
import discord
from pathlib import Path
from typing import List, Dict, Any
import logging


logger = logging.getLogger(__name__)


async def download_attachments(
    attachments: List[discord.Attachment],
    workspace: Path,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    timeout: int = 30,
) -> List[Dict[str, Any]]:
    """
    Discordの添付ファイルをワークスペースにダウンロード

    Args:
        attachments: Discord Attachmentオブジェクトのリスト
        workspace: ダウンロード先のワークスペースディレクトリ
        max_file_size: 最大ファイルサイズ（バイト）
        timeout: ダウンロードタイムアウト（秒）

    Returns:
        ダウンロード結果のリスト
        [
            {
                "success": bool,
                "filename": str,
                "path": str,
                "size": int,
                "error": str
            }
        ]
    """
    if not attachments:
        return []

    # workspaceディレクトリを確認
    workspace = Path(workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    results = []

    async with aiohttp.ClientSession() as session:
        tasks = [
            _download_attachment(
                session=session,
                attachment=attachment,
                workspace=workspace,
                max_file_size=max_file_size,
                timeout=timeout,
            )
            for attachment in attachments
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

    # 例外を結果形式に変換
    formatted_results = []
    for result in results:
        if isinstance(result, Exception):
            formatted_results.append(
                {
                    "success": False,
                    "filename": "",
                    "path": "",
                    "size": 0,
                    "error": str(result),
                }
            )
        else:
            formatted_results.append(result)

    return formatted_results


async def _download_attachment(
    session: aiohttp.ClientSession,
    attachment: discord.Attachment,
    workspace: Path,
    max_file_size: int,
    timeout: int,
) -> Dict[str, Any]:
    """
    個々の添付ファイルをダウンロード

    Args:
        session: aiohttpセッション
        attachment: Discord Attachmentオブジェクト
        workspace: ダウンロード先ディレクトリ
        max_file_size: 最大ファイルサイズ
        timeout: タイムアウト（秒）

    Returns:
        ダウンロード結果
    """
    filename = attachment.filename
    url = attachment.url
    file_size = attachment.size or 0

    # ファイルサイズチェック
    if file_size > max_file_size:
        return {
            "success": False,
            "filename": filename,
            "path": "",
            "size": file_size,
            "error": f"File too large: {file_size} bytes (max: {max_file_size})",
        }

    # ダウンロード先パス
    file_path = workspace / filename

    try:
        # ファイルをダウンロード
        async with session.get(
            url, timeout=aiohttp.ClientTimeout(total=timeout)
        ) as response:
            if response.status != 200:
                return {
                    "success": False,
                    "filename": filename,
                    "path": "",
                    "size": file_size,
                    "error": f"HTTP error: {response.status}",
                }

            # コンテンツサイズチェック
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > max_file_size:
                return {
                    "success": False,
                    "filename": filename,
                    "path": "",
                    "size": int(content_length),
                    "error": f"File too large: {content_length} bytes (max: {max_file_size})",
                }

            # ファイルに書き込み
            content = await response.read()

            if len(content) > max_file_size:
                return {
                    "success": False,
                    "filename": filename,
                    "path": "",
                    "size": len(content),
                    "error": f"File too large: {len(content)} bytes (max: {max_file_size})",
                }

            with open(file_path, "wb") as f:
                f.write(content)

            logger.info(f"Downloaded attachment: {filename} -> {file_path}")

            return {
                "success": True,
                "filename": filename,
                "path": str(file_path),
                "size": len(content),
                "error": "",
            }

    except asyncio.TimeoutError:
        return {
            "success": False,
            "filename": filename,
            "path": "",
            "size": file_size,
            "error": f"Download timeout after {timeout} seconds",
        }
    except (OSError, aiohttp.ClientError, discord.HTTPException) as e:
        logger.error(f"Error downloading attachment {filename}: {e}")
        return {
            "success": False,
            "filename": filename,
            "path": "",
            "size": file_size,
            "error": str(e),
        }


def format_attachments_summary(results: List[dict]) -> str:
    """
    添付ファイルのダウンロード結果を要約文字列に変換

    Args:
        results: download_attachmentsの結果リスト

    Returns:
        要約文字列
    """
    if not results:
        return ""

    lines = ["**添付ファイル:**"]

    for result in results:
        if result["success"]:
            lines.append(f"- ✅ `{result['filename']}` ({result['size']} bytes)")
        else:
            lines.append(f"- ❌ `{result['filename']}`: {result['error']}")

    return "\n".join(lines)
