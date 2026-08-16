from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.security import vault
from backend.app.database.models import AIApiKeyMetadata


def create_key_hint(key: str) -> str:
    """Generates a safe non-revealing hint for UI display (e.g. sk-...a1b2)."""
    if not key or len(key) < 8:
        return "••••••••"
    prefix = key[:3]
    suffix = key[-4:]
    return f"{prefix}...{suffix}"


class AIKeyManager:
    """Secure encrypted storage for external AI API keys."""

    @staticmethod
    async def store_key(session: AsyncSession, provider_name: str, plain_key: str) -> AIApiKeyMetadata:
        encrypted = vault.encrypt(plain_key)
        hint = create_key_hint(plain_key)

        stmt = select(AIApiKeyMetadata).where(AIApiKeyMetadata.provider_name == provider_name.upper())
        res = await session.execute(stmt)
        record = res.scalar_one_or_none()

        if not record:
            record = AIApiKeyMetadata(
                provider_name=provider_name.upper(),
                encrypted_key=encrypted,
                key_hint=hint
            )
            session.add(record)
        else:
            record.encrypted_key = encrypted
            record.key_hint = hint

        await session.commit()
        await session.refresh(record)
        return record

    @staticmethod
    async def get_decrypted_key(session: AsyncSession, provider_name: str) -> Optional[str]:
        stmt = select(AIApiKeyMetadata).where(AIApiKeyMetadata.provider_name == provider_name.upper())
        res = await session.execute(stmt)
        record = res.scalar_one_or_none()

        if not record or not record.encrypted_key:
            return None

        return vault.decrypt(record.encrypted_key)


ai_key_manager = AIKeyManager()
