# t.me/Smarty MS  <3
# Advanced Telegram Reporter - Fixed for Telethon 2026 / New Telegram API

from telethon import TelegramClient, functions, types
from telethon.errors import PhoneNumberInvalidError, FloodWaitError, PeerFloodError
from os import listdir, mkdir
from sys import argv
from re import search
from colorama import Fore, Style, init
import asyncio, argparse, random, time

init(autoreset=True)  # Colorama init

# ─── Argument Parser ───────────────────────────────────────────────────────────
argument_parser = argparse.ArgumentParser(
    description='Advanced Telegram Reporter by @Smarty MS',
    add_help=False
)
argument_parser.add_argument('-an', '--add-number', help='Add a new account')
argument_parser.add_argument('-r',  '--run',    help='Count of reports per account', type=int)
argument_parser.add_argument('-t',  '--target', help='Target channel (without @)',   type=str)
argument_parser.add_argument('-d',  '--delay',  help='Delay between reports in sec (default: random 1-4)', type=float, default=None)
argument_parser.add_argument(
    '-m', '--mode',
    help='Report reason',
    choices=['spam', 'fake_account', 'violence', 'child_abuse', 'pornography', 'geoirrelevant']
)
argument_parser.add_argument('-re', '--reasons', help='Show list of reasons', action='store_true')
argument_parser.add_argument('-h',  '--help',    action='store_true')

command_line_args = argument_parser.parse_args()

# ─── Sessions Folder ───────────────────────────────────────────────────────────
try:
    mkdir('sessions')
except Exception:
    pass

session_files = [f for f in listdir('sessions') if f.endswith('.session')]
session_files.sort()

# ─── API Credentials ───────────────────────────────────────────────────────────
api_id   = 25148883
api_hash = 'abc30c3b47a075ec9a0854b3015ef210'

# ─── Keyword hints for option-based API (Telegram 2025+) ──────────────────────
OPTION_KEYWORDS = {
    'spam':          ['spam', 'unwanted', 'advertis'],
    'fake_account':  ['fake', 'impersonat', 'fraud'],
    'violence':      ['violen', 'harm', 'threat'],
    'child_abuse':   ['child', 'minor', 'abuse', 'csam'],
    'pornography':   ['porn', 'adult', 'sexual', 'explicit', 'nude'],
    'geoirrelevant': ['geo', 'irrelevant', 'location', 'region'],
}

# ─── Global Stats ─────────────────────────────────────────────────────────────
stats = {'success': 0, 'failed': 0, 'errors': 0}

# ─── Banner ───────────────────────────────────────────────────────────────────
BANNER = f"""
{Fore.CYAN}
  __  __ ____     ____  ____   ___
 |  \\/  / ___|   | __ )|  _ \\ / _ \\
 | |\\/| \\___ \\   |  _ \\| |_) | | | |
 | |  | |___) |  | |_) |  _ <| |_| |
 |_|  |_|____/   |____/|_| \\_\\\\___/
{Fore.RESET}
{Fore.YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Fore.RESET}
  {Fore.MAGENTA}Advanced Telegram Reporter{Fore.RESET} by {Fore.CYAN}@Smarty MS{Fore.RESET}
  {Fore.WHITE}use --help : python3 {argv[0]} --help{Fore.RESET}
{Fore.YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Fore.RESET}
"""

# ─── Help ──────────────────────────────────────────────────────────────────────
if command_line_args.help:
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════╗
║         MS BRO Reporter - Help Menu          ║
╚══════════════════════════════════════════════╝{Fore.RESET}

  {Fore.LIGHTBLUE_EX}-an{Fore.RESET}, --add-number {Fore.YELLOW}NUMBER{Fore.RESET}
      Account add karo
      example: python3 {argv[0]} -an {Fore.LIGHTBLUE_EX}+911234567890{Fore.RESET}

  {Fore.LIGHTBLUE_EX}-r{Fore.RESET}, --run {Fore.YELLOW}COUNT{Fore.RESET}
      Reports ki count set karo (per account)

  {Fore.LIGHTBLUE_EX}-t{Fore.RESET}, --target {Fore.YELLOW}TARGET{Fore.RESET}
      Target channel (@ ke bina)

  {Fore.LIGHTBLUE_EX}-m{Fore.RESET}, --mode {Fore.YELLOW}MODE{Fore.RESET}
      Report reason set karo

  {Fore.LIGHTBLUE_EX}-d{Fore.RESET}, --delay {Fore.YELLOW}SECONDS{Fore.RESET}
      Reports ke beech delay (default: random 1-4s)

  {Fore.LIGHTBLUE_EX}-re{Fore.RESET}, --reasons
      Reasons ki list dekho

  example: python3 {argv[0]} -r {Fore.LIGHTBLUE_EX}1000{Fore.RESET} -t {Fore.LIGHTBLUE_EX}channelName{Fore.RESET} -m {Fore.LIGHTBLUE_EX}spam{Fore.RESET} -d {Fore.LIGHTBLUE_EX}2{Fore.RESET}
""")

# ─── Reasons list ─────────────────────────────────────────────────────────────
elif command_line_args.reasons:
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════╗
║            Report Reasons List               ║
╚══════════════════════════════════════════════╝{Fore.RESET}
    {Fore.YELLOW}[1]{Fore.RESET} spam
    {Fore.YELLOW}[2]{Fore.RESET} fake_account
    {Fore.YELLOW}[3]{Fore.RESET} violence
    {Fore.YELLOW}[4]{Fore.RESET} child_abuse
    {Fore.YELLOW}[5]{Fore.RESET} pornography
    {Fore.YELLOW}[6]{Fore.RESET} geoirrelevant
""")

# ─── Add Account ──────────────────────────────────────────────────────────────
elif command_line_args.add_number is not None:
    phone_number = command_line_args.add_number

    if session_files:
        nums = []
        for sf in session_files:
            m = search(r'Ac(\d+)\.session', sf)
            if m:
                nums.append(int(m.group(1)))
        next_num = (max(nums) + 1) if nums else 1
    else:
        next_num = 1

    async def add_account():
        print(f'\n {Fore.CYAN}[*]{Fore.RESET} Account add ho raha hai... Ac{next_num}')
        client = TelegramClient(f'sessions/Ac{next_num}', api_id, api_hash)
        try:
            await client.start(phone=lambda: phone_number)
            me = await client.get_me()
            name = me.first_name if me else "Unknown"
            print(f' [{Fore.GREEN}✅{Fore.RESET}] Account add ho gaya! {Fore.CYAN}{name}{Fore.RESET} -> Ac{next_num}')
        except PhoneNumberInvalidError:
            print(f' [{Fore.RED}✗{Fore.RESET}] Phone number invalid hai!')
        except Exception as e:
            print(f' [{Fore.RED}✗{Fore.RESET}] Error: {Fore.RED}{e}{Fore.RESET}')
        finally:
            await client.disconnect()

    asyncio.run(add_account())

# ─── Run Reports ──────────────────────────────────────────────────────────────
elif (
    command_line_args.add_number is None
    and command_line_args.run is not None
    and command_line_args.target is not None
    and command_line_args.mode is not None
):
    if not session_files:
        print(f' [{Fore.RED}✗{Fore.RESET}] Koi account nahi! Pehle add karo: python3 {argv[0]} -an +91XXXXXXXXXX')
        exit(0)

    report_count   = command_line_args.run
    target_channel = command_line_args.target
    selected_mode  = command_line_args.mode
    custom_delay   = command_line_args.delay
    report_message = f"This channel sends offensive content - {selected_mode}"
    start_time     = time.time()

    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════╗
║            MS BRO - Report Started           ║
╚══════════════════════════════════════════════╝{Fore.RESET}
  {Fore.WHITE}Target   :{Fore.RESET} {Fore.RED}@{target_channel}{Fore.RESET}
  {Fore.WHITE}Mode     :{Fore.RESET} {Fore.YELLOW}{selected_mode}{Fore.RESET}
  {Fore.WHITE}Count    :{Fore.RESET} {Fore.CYAN}{report_count} per account{Fore.RESET}
  {Fore.WHITE}Accounts :{Fore.RESET} {Fore.GREEN}{len(session_files)}{Fore.RESET}
  {Fore.WHITE}Delay    :{Fore.RESET} {Fore.CYAN}{"random 1-4s" if custom_delay is None else f"{custom_delay}s"}{Fore.RESET}
{Fore.YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Fore.RESET}""")

    async def pick_option(result, mode):
        """New Telegram API 2025+ - 2 step report flow"""
        if hasattr(result, 'options') and result.options:
            keywords = OPTION_KEYWORDS.get(mode, [mode])
            for opt in result.options:
                opt_text = (opt.text or '').lower()
                for kw in keywords:
                    if kw in opt_text:
                        return opt.option
            return result.options[0].option
        return None

    async def report_channel(client, session_name):
        global stats
        async with client:
            try:
                me = await client.get_me()
                user_name = me.first_name if me else session_name
            except Exception:
                user_name = session_name

            try:
                recent_messages = await client.get_messages(target_channel, limit=5)
            except ValueError:
                print(f' [{Fore.RED}✗{Fore.RESET}] Channel invalid: {target_channel}')
                return
            except Exception as e:
                print(f' [{Fore.RED}✗{Fore.RESET}] Fetch error ({user_name}): {e}')
                return

            message_ids = [msg.id for msg in recent_messages if msg and msg.id]
            if not message_ids:
                print(f' [{Fore.RED}✗{Fore.RESET}] Channel mein koi message nahi!')
                return

            # Join if not joined
            already_joined = False
            try:
                async for dialog in client.iter_dialogs():
                    if dialog.is_channel and dialog.entity.username == target_channel:
                        already_joined = True
                        break
            except Exception:
                pass

            if not already_joined:
                try:
                    from telethon.tl.functions.channels import JoinChannelRequest
                    await client(JoinChannelRequest(target_channel))
                    await asyncio.sleep(1)
                    print(f' [{Fore.CYAN}->{Fore.RESET}] {Fore.CYAN}{user_name}{Fore.RESET} joined @{target_channel}')
                except Exception as e:
                    print(f' [{Fore.YELLOW}!{Fore.RESET}] Join skip ({user_name}): {e}')

            # ── Report Loop ────────────────────────────────────────────────────
            consecutive_errors = 0
            for i in range(report_count):
                try:
                    # Step 1: Empty option -> get available options from Telegram
                    result = await client(functions.messages.ReportRequest(
                        peer=target_channel,
                        id=message_ids,
                        option=b'',
                        message=report_message
                    ))

                    # Step 2: Choose correct option by mode keywords
                    chosen_option = await pick_option(result, selected_mode)
                    if chosen_option is not None:
                        result = await client(functions.messages.ReportRequest(
                            peer=target_channel,
                            id=message_ids,
                            option=chosen_option,
                            message=report_message
                        ))

                    success = (
                        result is True
                        or hasattr(result, 'CONSTRUCTOR_ID')
                        or getattr(result, 'accepted', False)
                    )

                    if success or result:
                        stats['success'] += 1
                        consecutive_errors = 0
                        print(
                            f" [{Fore.GREEN}✅{Fore.RESET}] Reported!"
                            f"  {Fore.CYAN}{user_name}{Fore.RESET}"
                            f"  {Fore.YELLOW}{i+1}/{report_count}{Fore.RESET}"
                            f"  {Fore.GREEN}[Total: {stats['success']}]{Fore.RESET}"
                        )
                    else:
                        stats['failed'] += 1
                        print(
                            f" [{Fore.RED}✗{Fore.RESET}] Failed!"
                            f"  {Fore.CYAN}{user_name}{Fore.RESET}"
                            f"  {Fore.YELLOW}{i+1}/{report_count}{Fore.RESET}"
                        )

                except FloodWaitError as e:
                    wait = e.seconds + random.randint(1, 5)
                    print(f' [{Fore.YELLOW}!{Fore.RESET}] FloodWait! {Fore.YELLOW}{user_name}{Fore.RESET} -> {wait}s wait...')
                    await asyncio.sleep(wait)
                    continue

                except PeerFloodError:
                    print(f' [{Fore.RED}✗{Fore.RESET}] PeerFlood! {Fore.RED}{user_name}{Fore.RESET} blocked by Telegram. 30s wait...')
                    await asyncio.sleep(30)
                    consecutive_errors += 1

                except Exception as e:
                    stats['errors'] += 1
                    consecutive_errors += 1
                    print(f' [{Fore.RED}✗{Fore.RESET}] Error ({user_name}) #{i+1}: {Fore.RED}{e}{Fore.RESET}')
                    await asyncio.sleep(3)

                # 5 consecutive errors -> skip this account
                if consecutive_errors >= 5:
                    print(f' [{Fore.RED}✗{Fore.RESET}] {user_name} -> 5 consecutive errors, skipping.')
                    break

                # Delay - random ya fixed
                delay = custom_delay if custom_delay is not None else random.uniform(1.0, 4.0)
                await asyncio.sleep(delay)

    async def run_all_accounts():
        tasks = []
        for sf in session_files:
            session_path = f"sessions/{sf[:-8]}"
            client = TelegramClient(session_path, api_id, api_hash)
            tasks.append(report_channel(client, sf))
        if tasks:
            await asyncio.gather(*tasks)
        else:
            print(f' [{Fore.RED}✗{Fore.RESET}] Koi valid session nahi mili!')

        # ── Final Summary ──────────────────────────────────────────────────────
        elapsed = round(time.time() - start_time, 1)
        total   = stats['success'] + stats['failed'] + stats['errors']
        print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════╗
║               Report Summary                 ║
╚══════════════════════════════════════════════╝{Fore.RESET}
  {Fore.GREEN}✅ Success  :{Fore.RESET} {stats['success']}
  {Fore.RED}✗  Failed   :{Fore.RESET} {stats['failed']}
  {Fore.YELLOW}!  Errors   :{Fore.RESET} {stats['errors']}
  {Fore.WHITE}   Total    :{Fore.RESET} {total}
  {Fore.WHITE}   Time     :{Fore.RESET} {elapsed}s
{Fore.YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Fore.RESET}
  {Fore.MAGENTA}by @Smarty MS{Fore.RESET}
""")

    asyncio.run(run_all_accounts())

# ─── Missing args ──────────────────────────────────────────────────────────────
elif (
    command_line_args.add_number is None
    and command_line_args.run is not None
    and (command_line_args.target is None or command_line_args.mode is None)
):
    print(
        f"\n [{Fore.RED}✗{Fore.RESET}] Sahi format:{Fore.RED} -> {Fore.RESET}"
        f"python3 {argv[0]} -r 500 -t channelName -m spam\n"
    )

# ─── Default Banner ───────────────────────────────────────────────────────────
else:
    print(BANNER)
