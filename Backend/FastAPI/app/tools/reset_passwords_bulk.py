import os
import sys
import json
import argparse
import asyncio
from datetime import datetime
from typing import List, Tuple, Optional

import asyncpg
import bcrypt


def _normalize_dsn(url: str) -> str:
    """Normalize SQLAlchemy-style DSNs to asyncpg-compatible ones."""
    if url.startswith("postgresql+asyncpg://"):
        return "postgresql://" + url.split("postgresql+asyncpg://", 1)[1]
    if url.startswith("postgres+asyncpg://"):
        return "postgres://" + url.split("postgres+asyncpg://", 1)[1]
    return url


def build_dsn() -> str:
    """Build PostgreSQL DSN from env vars or DATABASE_URL."""
    # Prefer explicit DB params, fall back to FASTAPI_DATABASE_URL/DATABASE_URL
    url = os.getenv("FASTAPI_DATABASE_URL") or os.getenv("DATABASE_URL")
    if url:
        return _normalize_dsn(url)

    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    db = os.getenv("POSTGRES_DB", "postgres")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def make_bcrypt_hash(password: str, rounds: int = 12) -> str:
    """Generate a bcrypt hash with $2b$ and the given rounds."""
    salt = bcrypt.gensalt(rounds)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def parse_user_list_from_file(path: str) -> List[Tuple[str, Optional[str]]]:
    """Parse usernames (and optional passwords) from a file.

    Supported formats:
    - JSON array of usernames: ["user1", "user2"]
    - JSON object mapping: {"user1": "pass1", "user2": "pass2"}
    - Newline text: one username per line
    - CSV: username,password per line
    """
    content = open(path, "r", encoding="utf-8").read().strip()
    entries: List[Tuple[str, Optional[str]]] = []

    # Try JSON first
    try:
        data = json.loads(content)
        if isinstance(data, list):
            for u in data:
                if isinstance(u, str) and u:
                    entries.append((u.strip(), None))
        elif isinstance(data, dict):
            for u, p in data.items():
                if isinstance(u, str) and u:
                    pw = p if isinstance(p, str) else None
                    entries.append((u.strip(), pw))
        if entries:
            return entries
    except Exception:
        pass

    # Try CSV (username,password)
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    for line in lines:
        if "," in line:
            u, p = [x.strip() for x in line.split(",", 1)]
            if u:
                entries.append((u, p or None))
        else:
            # Plain newline list of usernames
            entries.append((line, None))

    return entries


async def set_user_password(conn: asyncpg.Connection, username: str, hash_value: str, actor: str) -> bool:
    """Update a single user's password; return True if updated."""
    try:
        row = await conn.fetchrow(
            'UPDATE "SEC"."Usuario" '\
            'SET senha=$1, cadastranteupdate=$2, dataupdate=CURRENT_TIMESTAMP '\
            'WHERE usuario=$3 '\
            'RETURNING usuario, senha',
            hash_value,
            actor,
            username,
        )
        return row is not None
    except Exception as e:
        print(f"[ERROR] Failed to update user '{username}': {e}")
        return False


async def verify_prefix(conn: asyncpg.Connection, username: str, expected_prefix: str = "$2b$") -> bool:
    """Verify stored hash prefix for the given user."""
    try:
        row = await conn.fetchrow(
            'SELECT senha FROM "SEC"."Usuario" WHERE usuario=$1', username
        )
        if not row:
            print(f"[WARN] User '{username}' not found during verification.")
            return False
        stored = row["senha"]
        ok = isinstance(stored, str) and stored.startswith(expected_prefix)
        print(f"[VERIFY] {username}: prefix_ok={ok}")
        return ok
    except Exception as e:
        print(f"[ERROR] Verification failed for '{username}': {e}")
        return False


async def bulk_reset(user_entries: List[Tuple[str, Optional[str]]], default_password: str, rounds: int, actor: str, dry_run: bool) -> dict:
    """Perform bulk password resets."""
    dsn = build_dsn()
    pool = await asyncpg.create_pool(dsn)
    results = {"updated": [], "skipped": [], "failed": []}

    async with pool.acquire() as conn:
        for username, pw in user_entries:
            password = pw or default_password
            if dry_run:
                print(f"[DRY-RUN] Would reset '{username}' with $2b${rounds}")
                results["skipped"].append(username)
                continue

            try:
                hash_value = make_bcrypt_hash(password, rounds)
                # Sanity check prefix
                if not hash_value.startswith("$2b$"):
                    print(f"[ERROR] Generated hash for '{username}' has unexpected prefix: {hash_value[:4]}")
                    results["failed"].append(username)
                    continue

                updated = await set_user_password(conn, username, hash_value, actor)
                if updated:
                    # Immediate verification
                    await verify_prefix(conn, username, "$2b$")
                    results["updated"].append(username)
                else:
                    print(f"[WARN] User '{username}' not found; no rows updated.")
                    results["failed"].append(username)
            except Exception as e:
                print(f"[ERROR] Exception resetting '{username}': {e}")
                results["failed"].append(username)

    await pool.close()
    return results


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Bulk reset user passwords to bcrypt $2b$ with specified rounds")
    parser.add_argument("--usernames", help="Lista de usernames separados por vírgula", default="")
    parser.add_argument("--file", help="Arquivo com lista de usuários (json/csv/txt)")
    parser.add_argument("--password", help="Senha padrão para os usuários (default: Admin123)", default="Admin123")
    parser.add_argument("--rounds", type=int, help="Custo do bcrypt (rounds)", default=12)
    parser.add_argument("--actor", help="Identificador de quem executa (CadastranteUpdate)", default="SEC::BULK_RESET")
    parser.add_argument("--dry-run", action="store_true", help="Executa sem aplicar updates, só imprime")

    args = parser.parse_args(argv)

    entries: List[Tuple[str, Optional[str]]] = []
    if args.usernames:
        for u in [x.strip() for x in args.usernames.split(",") if x.strip()]:
            entries.append((u, None))
    if args.file:
        entries.extend(parse_user_list_from_file(args.file))

    if not entries:
        print("[ERROR] Nenhum usuário fornecido (--usernames ou --file)")
        return 2

    print(f"[INFO] Início do reset em massa | total={len(entries)} | rounds={args.rounds} | actor={args.actor} | dry_run={args.dry_run}")
    results = asyncio.get_event_loop().run_until_complete(
        bulk_reset(entries, args.password, args.rounds, args.actor, args.dry_run)
    )
    print("[SUMMARY] Atualizados:", len(results["updated"]))
    print("[SUMMARY] Falhas:", len(results["failed"]))
    print("[SUMMARY] Skipped (dry-run):", len(results["skipped"]))
    if results["failed"]:
        print("[FAILED USERS]", ", ".join(results["failed"]))
    if results["updated"]:
        print("[UPDATED USERS]", ", ".join(results["updated"]))
    return 0 if not results["failed"] else 1


if __name__ == "__main__":
    sys.exit(main())