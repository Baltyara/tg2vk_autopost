import asyncio
import argparse
from opentele.td import TDesktop
from opentele.api import UseCurrentSession


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("tdata_path")
    ap.add_argument("api_id", type=int)
    ap.add_argument("api_hash")
    args = ap.parse_args()

    tdesk = TDesktop(args.tdata_path)
    client = await tdesk.ToTelethon(
        session="telethon.session",
        flag=UseCurrentSession,
        api_id=args.api_id,
        api_hash=args.api_hash,
    )
    # Save string session
    print(client.session.save())


if __name__ == "__main__":
    asyncio.run(main())


