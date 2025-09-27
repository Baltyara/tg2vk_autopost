import sys
import argparse
from telethon.sync import TelegramClient
from telethon.sessions import StringSession


API_ID = 27435631
API_HASH = 'c88866acc346c546dc2061f33414ff9c'


def norm_phone(phone: str) -> str:
    p = phone.strip()
    if p.startswith('+'):
        return p
    if p.startswith('8') and len(p) == 11:
        return '+7' + p[1:]
    if p.startswith('7') and len(p) == 11:
        return '+' + p
    return '+7' + p


def cmd_request_code(phone: str) -> None:
    phone = norm_phone(phone)
    with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        client.send_code_request(phone)
        print('OK:CODE_SENT')


def cmd_sign_in(phone: str, code: str, password: str | None) -> None:
    phone = norm_phone(phone)
    with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        if password:
            client.sign_in(phone=phone, code=code, password=password)
        else:
            client.sign_in(phone=phone, code=code)
        print(client.session.save())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--step', required=True, choices=['request', 'signin'])
    ap.add_argument('--phone', required=True)
    ap.add_argument('--code')
    ap.add_argument('--password')
    args = ap.parse_args()

    if args.step == 'request':
        cmd_request_code(args.phone)
    else:
        if not args.code:
            print('ERROR: code required', file=sys.stderr)
            sys.exit(2)
        cmd_sign_in(args.phone, args.code, args.password)


if __name__ == '__main__':
    main()


