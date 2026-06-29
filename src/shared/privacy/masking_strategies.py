#!/usr/bin/env python3
"""
MSRA 脱敏策略实现

提供各类 PII 的脱敏处理函数，支持部分隐藏、完全隐藏、哈希替换等策略。
所有脱敏函数保持幂等性——对已脱敏值重复调用不会产生错误结果。
"""

import hashlib
import secrets
from typing import Optional


class MaskingStrategies:
    """脱敏策略集合"""

    # ── 身份证号 ──

    @staticmethod
    def mask_id_card(value: str, show_prefix: int = 3, show_suffix: int = 4) -> str:
        """身份证号部分隐藏

        Args:
            value: 原始身份证号
            show_prefix: 保留前 N 位（默认 3）
            show_suffix: 保留后 N 位（默认 4）

        Returns:
            脱敏后的值，如 "110***********1234"
        """
        if not value or len(str(value)) < 8:
            return value
        s = str(value)
        mask_len = len(s) - show_prefix - show_suffix
        if mask_len <= 0:
            return s
        return s[:show_prefix] + "*" * mask_len + s[-show_suffix:]

    # ── 手机号 ──

    @staticmethod
    def mask_phone(value: str) -> str:
        """手机号部分隐藏: 138****8000"""
        if not value or len(str(value)) != 11:
            return value
        s = str(value)
        return s[:3] + "****" + s[7:]

    # ── 邮箱 ──

    @staticmethod
    def mask_email(value: str) -> str:
        """邮箱部分隐藏: t***@example.com"""
        if not value or "@" not in str(value):
            return value
        s = str(value)
        local, domain = s.rsplit("@", 1)
        if len(local) <= 1:
            return "*" * 3 + "@" + domain
        return local[0] + "***@" + domain

    # ── 银行卡号 ──

    @staticmethod
    def mask_bank_card(value: str) -> str:
        """银行卡号部分隐藏: **** **** **** 0123"""
        if not value or len(str(value)) < 8:
            return value
        s = str(value).replace(" ", "")
        return "*" * (len(s) - 4) + s[-4:]

    # ── IP 地址 ──

    @staticmethod
    def mask_ip(value: str) -> str:
        """IP 地址部分隐藏: 192.168.*.*"""
        if not value:
            return value
        parts = str(value).split(".")
        if len(parts) != 4:
            return value
        return f"{parts[0]}.{parts[1]}.*.*"

    # ── 护照号 ──

    @staticmethod
    def mask_passport(value: str) -> str:
        """护照号部分隐藏: E*******8"""
        if not value or len(str(value)) < 4:
            return value
        s = str(value)
        return s[0] + "*" * (len(s) - 2) + s[-1]

    # ── 通用完全隐藏 ──

    @staticmethod
    def mask_full(value: str, replacement: str = "[REDACTED]") -> str:
        """完全替换为 [REDACTED]"""
        return replacement

    # ── 哈希替换（不可逆）──

    @staticmethod
    def hash_value(value: str, salt: Optional[str] = None, length: int = 16) -> str:
        """SHA-256 哈希替换（不可逆）

        Args:
            value: 原始值
            salt: 盐值（None 时使用随机盐，结果不可复现）
            length: 哈希截取长度

        Returns:
            哈希后的十六进制字符串
        """
        if not value:
            return value
        if salt is None:
            salt = secrets.token_hex(8)
        h = hashlib.sha256(f"{salt}{value}".encode("utf-8")).hexdigest()
        return h[:length]

    # ── 保留原样 ──

    @staticmethod
    def keep(value: str) -> str:
        """保留原样（仅记录决策，不做修改）"""
        return value

    # ── 日期偏移 ──

    @staticmethod
    def offset_date(value: str, max_days: int = 7) -> str:
        """日期随机偏移（±max_days 天），保留时间间隔

        注意：此方法返回占位符，实际偏移需在 DataFrame 层面用 pd.to_datetime 处理。
        """
        # 标记为需要日期偏移处理，具体实现在 DataFrame 级别
        return f"[DATE_OFFSET_±{max_days}d]"

    # ── 策略分发表 ──

    @classmethod
    def apply(cls, value: str, pii_type: str, action: str, **kwargs) -> str:
        """根据 PII 类型和动作分发到对应脱敏函数

        Args:
            value: 原始值
            pii_type: PII 类型（id_card / phone / email / bank_card / ip / passport）
            action: 脱敏动作（mask_partial / mask_full / hash / keep）

        Returns:
            脱敏后的值
        """
        if action == "keep":
            return cls.keep(value)
        if action == "mask_full":
            return cls.mask_full(value, kwargs.get("replacement", "[REDACTED]"))
        if action == "hash":
            return cls.hash_value(value, kwargs.get("salt"), kwargs.get("length", 16))

        # mask_partial: 按类型选择部分隐藏函数
        partial_map = {
            "id_card": cls.mask_id_card,
            "phone": cls.mask_phone,
            "email": cls.mask_email,
            "bank_card": cls.mask_bank_card,
            "ip": cls.mask_ip,
            "passport": cls.mask_passport,
        }
        func = partial_map.get(pii_type)
        if func:
            return func(value)
        # 未知类型: 默认完全隐藏
        return cls.mask_full(value)
