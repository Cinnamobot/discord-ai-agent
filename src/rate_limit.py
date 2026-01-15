"""レート制限モジュール"""

import time
from collections import defaultdict
from typing import Tuple


class RateLimiter:
    """リクエストのレート制限を行うクラス"""

    def __init__(self, per_minute: int = 10, per_hour: int = 100):
        """
        初期化

        Args:
            per_minute: 1分間あたりの最大リクエスト数
            per_hour: 1時間あたりの最大リクエスト数
        """
        self.per_minute = per_minute
        self.per_hour = per_hour
        self.requests: dict[int, list[float]] = defaultdict(list)

    async def check_rate_limit(self, user_id: int) -> Tuple[bool, str]:
        """
        レート制限チェック

        Args:
            user_id: ユーザーID

        Returns:
            (許可されるかどうか, エラーメッセージ)
        """
        now = time.time()
        user_requests = self.requests[user_id]

        # 古いリクエストを削除（1時間以上前のもの）
        self.requests[user_id] = [r for r in user_requests if now - r < 3600]
        user_requests = self.requests[user_id]

        # 1分間のチェック
        minute_ago = now - 60
        minute_count = sum(1 for r in user_requests if r > minute_ago)
        if minute_count >= self.per_minute:
            remaining = int(60 - (now - min(r for r in user_requests if r > minute_ago)))
            return False, f"レート制限: 1分間あたり{self.per_minute}リクエストまで。あと{remaining}秒お待ちください。"

        # 1時間のチェック
        if len(user_requests) >= self.per_hour:
            # 最も古いリクエストからの経過時間を計算
            oldest_request = min(user_requests)
            remaining = int(3600 - (now - oldest_request))
            return False, f"レート制限: 1時間あたり{self.per_hour}リクエストまで。あと{remaining}秒お待ちください。"

        # リクエストを記録
        self.requests[user_id].append(now)
        return True, ""

    def cleanup(self, max_age_seconds: int = 3600) -> int:
        """
        古いリクエストデータをクリーンアップ

        Args:
            max_age_seconds: 保持する最大秒数

        Returns:
            削除されたエントリ数
        """
        now = time.time()
        removed = 0

        for user_id in list(self.requests.keys()):
            self.requests[user_id] = [
                r for r in self.requests[user_id]
                if now - r < max_age_seconds
            ]
            if not self.requests[user_id]:
                del self.requests[user_id]
                removed += 1

        return removed
