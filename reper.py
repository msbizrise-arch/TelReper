# t.me/Mr3rf1  <3
# Updated & fixed version – March 2026 compatible
# Author: original @Mr3rf1, fixed & modernized

import asyncio
import argparse
import re
from os import listdir, mkdir
from sys import argv

from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ReportRequest
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError, FloodWaitError
from colorama import Fore, init

init(autoreset=True)  # initialize colorama

# -------------------------------------------------------------
#   CONFIG
# -------------------------------------------------------------
API_ID = 25148883
API_HASH = 'abc30c3b47a075ec9a0854b3015ef210'

SESSIONS_DIR = 'sessions'

# -------------------------------------------------------------
#   ARGUMENT PARSER
# -------------------------------------------------------------
parser = argparse.ArgumentParser(
    description='Telegram channel reporting tool (fixed 2026 version)',
    add_help=False
)

parser.add_argument('-an', '--add-number', help='Add new account (phone number)')
parser.add_argument('-r', '--run', type=int, help='Number of reports to send')
parser.add_argument('-t', '--target', help='Target channel username (without @)')
parser.add_argument('-m', '--mode', choices=[
    'spam', 'fake_account', 'violence', 'child_abuse', 'pornography', 'geoirrelevant'
], help='Report reason')
parser.add_argument('-re', '--reasons', action='store_true', help='Show available reasons')
parser.add_argument('-h', '--help', action='store_true', help='Show help')

args = parser.parse_args()

# -------------------------------------------------------------
#   HELP & REASONS
# -------------------------------------------------------------
if args.help:
    print(f'''
Help:
  -an NUMBER, --add-number NUMBER  →  Add new account
      example: python3 {argv[0]} -an +989123456789

  -r COUNT, --run COUNT            →  Number of reports
  -t TARGET, --target TARGET       →  Channel username (no @)
  -m MODE, --mode MODE             →  Report reason

      example: python3 {argv[0]} -r 500 -t testchannel -m spam

  -re, --reasons                   →  List of valid reasons
  -h, --help                       →  Show this help
''')
    exit(0)

if args.reasons:
    print(f'''
Available reasons:
    {Fore.YELLOW}spam{Fore.RESET}
    {Fore.YELLOW}fake_account{Fore.RESET}
    {Fore.YELLOW}violence{Fore.RESET}
    {Fore.YELLOW}child_abuse{Fore.RESET}
    {Fore.YELLOW}pornography{Fore.RESET}
    {Fore.YELLOW}geoirrelevant{Fore.RESET}
''')
    exit(0)

# -------------------------------------------------------------
#   CREATE SESSIONS FOLDER
# -------------------------------------------------------------
try:
    mkdir(SESSIONS_DIR)
except FileExistsError:
    pass

# -------------------------------------------------------------
#   ADD NEW ACCOUNT
# -------------------------------------------------------------
if args.add_number:
    phone = args.add_number.strip()

    session_files = [f for f in listdir(SESSIONS_DIR) if f.endswith('.session')]
    session_files.sort(key=lambda x: int(re.search(r'Ac(\d+)', x).group(1)) if re.search(r'Ac(\d+)', x) else 0)

    next_num = 1
    if session_files:
        last = session_files[-1]
        match = re.search(r'Ac(\d+)', last)
        if match:
            next_num = int(match.group(1)) + 1

    session_name = f"{SESSIONS_DIR}/Ac{next_num}"

    client = TelegramClient(session_name, API_ID, API_HASH)

    try:
        client.start(phone=phone)
        print(f"[{Fore.GREEN}OK{Fore.RESET}] Account added successfully → {session_name}")
    except PhoneNumberInvalidError:
        print(f"[{Fore.RED}ERROR{Fore.RESET}] Invalid phone number")
    except Exception as e:
        print(f"[{Fore.RED}ERROR{Fore.RESET}] {e}")
    finally:
        client.disconnect()
    exit(0)

# -------------------------------------------------------------
#   RUN REPORTING
# -------------------------------------------------------------
if args.run and args.target and args.mode:
    report_count = args.run
    target = args.target.strip()
    reason = args.mode

    session_files = [f for f in listdir(SESSIONS_DIR) if f.endswith('.session')]
    if not session_files:
        print(f"[{Fore.RED}ERROR{Fore.RESET}] No accounts found. Add at least one with -an")
        exit(1)

    async def report_with_account(session_file):
        client = TelegramClient(f"{SESSIONS_DIR}/{session_file}", API_ID, API_HASH)

        try:
            await client.connect()
            if not await client.is_user_authorized():
                print(f"[{Fore.YELLOW}WARN{Fore.RESET}] Session {session_file} not authorized")
                return

            me = await client.get_me()
            name = me.first_name or me.username or "Unknown"

            # Try to get entity (channel)
            try:
                entity = await client.get_entity(target)
            except Exception:
                print(f"[{Fore.RED}ERROR{Fore.RESET}] Cannot find channel @{target}")
                return

            # Join if not member
            if not hasattr(entity, 'username') or entity.username != target:
                await client(JoinChannelRequest(target))
                await asyncio.sleep(1.5)

            # Get some message IDs (needed for report)
            messages = await client.get_messages(entity, limit=3)
            msg_ids = [m.id for m in messages if m.id]

            if not msg_ids:
                print(f"[{Fore.YELLOW}WARN{Fore.RESET}] No messages found in channel")
                msg_ids = [0]  # fallback

            success_count = 0
            for i in range(report_count):
                try:
                    await client(ReportRequest(
                        peer=entity,
                        id=msg_ids,
                        option=b'',           # Telegram returns available options
                        message=f"Automated report - {reason}"
                    ))
                    success_count += 1
                    print(f"[{Fore.GREEN}OK{Fore.RESET}] Reported by {name} | {success_count}/{report_count}")
                    await asyncio.sleep(1.2 + (i % 5) * 0.3)  # random delay to avoid flood
                except FloodWaitError as e:
                    print(f"[{Fore.RED}FLOOD{Fore.RESET}] Wait {e.seconds}s")
                    await asyncio.sleep(e.seconds + 5)
                except Exception as e:
                    print(f"[{Fore.RED}ERROR{Fore.RESET}] {e}")
                    break

            print(f"[{Fore.CYAN}DONE{Fore.RESET}] Account {name} finished – {success_count} reports sent")

        except Exception as e:
            print(f"[{Fore.RED}CRITICAL{Fore.RESET}] Account {session_file} failed: {e}")
        finally:
            await client.disconnect()

    async def main():
        tasks = []
        for sess in session_files:
            tasks.append(report_with_account(sess))
        await asyncio.gather(*tasks, return_exceptions=True)

    print(f"[{Fore.CYAN}START{Fore.RESET}] Reporting @{target} with reason '{reason}' – {report_count} attempts")
    asyncio.run(main())

else:
    print(f"[{Fore.RED}USAGE ERROR{Fore.RESET}] Missing arguments.")
    print("Example: python3 reper.py -r 500 -t badchannel -m spam")
    print("Run with --help for full usage")
