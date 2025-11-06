import os
import sys
import argparse
import asyncio

import asyncpg
import bcrypt


def build_dsn() -> str:
    user = os.getenv("POSTGRES_USER", "admin")
    password = os.getenv("POSTGRES_PASSWORD", "admin")
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "SEC")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def make_hash(password: str, rounds: int, ident: str) -> str:
    salt = bcrypt.gensalt(rounds=rounds, prefix=ident.encode("utf-8"))
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


async def set_password(username: str, new_hash: str) -> None:
    dsn = build_dsn()
    conn = await asyncpg.connect(dsn)
    try:
        await conn.execute(
            'UPDATE "SEC"."Usuario" SET senha = $1, cadastranteupdate = $2, dataupdate = CURRENT_TIMESTAMP WHERE usuario = $3',
            new_hash,
            "SYSTEM",
            username,
        )
    finally:
        await conn.close()


async def verify_prefix(username: str) -> str:
    dsn = build_dsn()
    conn = await asyncpg.connect(dsn)
    try:
        row = await conn.fetchrow('SELECT senha FROM "SEC"."Usuario" WHERE usuario = $1', username)
        return row[0] if row else ""
    finally:
        await conn.close()


def main():
    parser = argparse.ArgumentParser(description="Reset password for a user in SEC.Usuario with bcrypt")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--rounds", type=int, default=12)
    parser.add_argument("--ident", default="2b", choices=["2a", "2b", "2y"])
    args = parser.parse_args()

    new_hash = make_hash(args.password, args.rounds, args.ident)
    print(f"Generated hash: {new_hash}")

    asyncio.run(set_password(args.username, new_hash))
    stored = asyncio.run(verify_prefix(args.username))
    print(f"Stored hash: {stored}")
    if stored.startswith(f"${args.ident}${args.rounds:02d}$"):
        print("OK: Stored hash has expected prefix.")
        sys.exit(0)
    else:
        print("ERROR: Stored hash prefix mismatch.")
        sys.exit(1)


if __name__ == "__main__":
    main()