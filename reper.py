# t.me/Mr3rf1  <3
# Fixed for Telethon 2026 / New Telegram API by Claude

from telethon import TelegramClient, functions, types
from telethon.errors import PhoneNumberInvalidError
from os import listdir, mkdir
from sys import argv
from re import search, findall
from colorama import Fore, init
import asyncio, argparse

init(autoreset=True)  # Colorama init - Windows ke liye zaroori

# ─── Argument Parser ───────────────────────────────────────────────────────────
argument_parser = argparse.ArgumentParser(
    description='A tool for reporting telegram channels by t.me/mr3rf1',
    add_help=False
)
argument_parser.add_argument('-an', '--add-number', help='Add a new account')
argument_parser.add_argument('-r', '--run', help='To get count and run', type=int)
argument_parser.add_argument('-t', '--target', help='Enter target', type=str)
argument_parser.add_argument(
    '-m', '--mode',
    help='Set reason of reports',
    choices=['spam', 'fake_account', 'violence', 'child_abuse', 'pornography', 'geoirrelevant']
)
argument_parser.add_argument('-re', '--reasons', help='Shows list of reasons', action='store_true')
argument_parser.add_argument('-h', '--help', action='store_true')

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

# ─── Mode → Telegram Report Reason mapping ─────────────────────────────────────
REASON_MAP = {
    'spam':         types.InputReportReasonSpam(),
    'fake_account': types.InputReportReasonFake(),
    'violence':     types.InputReportReasonViolence(),
    'child_abuse':  types.InputReportReasonChildAbuse(),
    'pornography':  types.InputReportReasonPornography(),
    'geoirrelevant':types.InputReportReasonGeoIrrelevant(),
}

# ─── Keyword hints for option-based API (new Telegram 2025+) ──────────────────
OPTION_KEYWORDS = {
    'spam':         ['spam', 'unwanted'],
    'fake_account': ['fake', 'impersonat'],
    'violence':     ['violen', 'harm'],
    'child_abuse':  ['child', 'minor', 'abuse'],
    'pornography':  ['porn', 'adult', 'sexual', 'explicit'],
    'geoirrelevant':['geo', 'irrelevant', 'location'],
}

# ─── Help ──────────────────────────────────────────────────────────────────────
if command_line_args.help:
    print(f'''Help:
  -an {Fore.LIGHTBLUE_EX}NUMBER{Fore.RESET}, --add-number {Fore.LIGHTBLUE_EX}NUMBER{Fore.RESET} ~> {Fore.YELLOW}add account to script{Fore.RESET}
  example: python3 {argv[0]} -an {Fore.LIGHTBLUE_EX}+1512****{Fore.RESET}

  -r {Fore.LIGHTBLUE_EX}COUNT{Fore.RESET}, --run {Fore.LIGHTBLUE_EX}COUNT{Fore.RESET} ~> {Fore.YELLOW}set count of reports{Fore.RESET}
  -t {Fore.LIGHTBLUE_EX}TARGET{Fore.RESET}, --target {Fore.LIGHTBLUE_EX}TARGET{Fore.RESET} ~> {Fore.YELLOW}set target (without @){Fore.RESET}
  -m {Fore.LIGHTBLUE_EX}MODE{Fore.RESET}, --mode {Fore.LIGHTBLUE_EX}MODE{Fore.RESET} ~> {Fore.YELLOW}set type of reports (spam,...){Fore.RESET}
  example: python3 {argv[0]} -r {Fore.LIGHTBLUE_EX}1000{Fore.RESET} -t {Fore.LIGHTBLUE_EX}mmdChannel{Fore.RESET} -m {Fore.LIGHTBLUE_EX}spam{Fore.RESET}

  -re, --reasons ~> {Fore.YELLOW}show list of reasons for reporting{Fore.RESET}
  -h, --help ~> {Fore.YELLOW}show help{Fore.RESET}''')

# ─── Reasons list ─────────────────────────────────────────────────────────────
elif command_line_args.reasons:
    print(f'''List of reasons:
    {Fore.YELLOW}*{Fore.RESET} spam
    {Fore.YELLOW}*{Fore.RESET} fake_account
    {Fore.YELLOW}*{Fore.RESET} violence
    {Fore.YELLOW}*{Fore.RESET} child_abuse
    {Fore.YELLOW}*{Fore.RESET} pornography
    {Fore.YELLOW}*{Fore.RESET} geoirrelevant''')

# ─── Add Account ──────────────────────────────────────────────────────────────
elif command_line_args.add_number is not None:
    phone_number = command_line_args.add_number

    # Next account number determine karo
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
        client = TelegramClient(f'sessions/Ac{next_num}', api_id, api_hash)
        try:
            await client.start(phone=lambda: phone_number)
            print(f' [{Fore.GREEN}✅{Fore.RESET}] Account successfully add ho gaya! Ac{next_num}')
        except PhoneNumberInvalidError:
            print(f' [{Fore.RED}!{Fore.RESET}] Phone number invalid hai!')
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
        print(f' [{Fore.RED}!{Fore.RESET}] Pehle account add karo: python3 {argv[0]} -an +91XXXXXXXXXX')
        exit(0)

    report_count    = command_line_args.run
    target_channel  = command_line_args.target
    selected_mode   = command_line_args.mode
    report_message  = f"This channel sends offensive content - {selected_mode}"

    async def pick_option_from_result(result, mode):
        """
        New Telegram API (2025+) mein ReportRequest pehle options return karta hai.
        Sahi option choose karke second call karo.
        """
        # Agar result mein 'options' attribute hai (ReportResultChooseOption)
        if hasattr(result, 'options') and result.options:
            keywords = OPTION_KEYWORDS.get(mode, [mode])
            for opt in result.options:
                opt_text = (opt.text or '').lower()
                for kw in keywords:
                    if kw in opt_text:
                        return opt.option
            # Koi match nahi mila - pehla option use karo
            return result.options[0].option
        return None

    async def report_channel(client, session_name):
        async with client:
            try:
                me = await client.get_me()
                user_name = me.first_name if me else session_name
            except Exception:
                user_name = session_name

            # Target channel validate karo
            try:
                recent_messages = await client.get_messages(target_channel, limit=5)
            except ValueError:
                print(f' [{Fore.RED}!{Fore.RESET}] Channel link invalid hai: {target_channel}')
                return
            except Exception as e:
                print(f' [{Fore.RED}!{Fore.RESET}] Channel fetch error: {e}')
                return

            message_ids = [msg.id for msg in recent_messages if msg and msg.id]
            if not message_ids:
                print(f' [{Fore.RED}!{Fore.RESET}] Koi message nahi mila channel mein!')
                return

            # Channel join karo agar already join nahi hai
            already_joined = False
            async for dialog in client.iter_dialogs():
                if dialog.is_channel and dialog.entity.username == target_channel:
                    already_joined = True
                    break
            if not already_joined:
                try:
                    from telethon.tl.functions.channels import JoinChannelRequest
                    await client(JoinChannelRequest(target_channel))
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f' [{Fore.YELLOW}⚠{Fore.RESET}] Join nahi hua ({e}), phir bhi try karta hoon...')

            # ── Report Loop ────────────────────────────────────────────────────
            for i in range(report_count):
                try:
                    # Step 1: Pehle option=b'' se call karo (new API flow)
                    result = await client(functions.messages.ReportRequest(
                        peer=target_channel,
                        id=message_ids,
                        option=b'',
                        message=report_message
                    ))

                    # Step 2: Agar options mili hain to sahi option choose karo
                    chosen_option = await pick_option_from_result(result, selected_mode)

                    if chosen_option is not None:
                        # Second call with actual option
                        result = await client(functions.messages.ReportRequest(
                            peer=target_channel,
                            id=message_ids,
                            option=chosen_option,
                            message=report_message
                        ))

                    # Success check
                    success = (
                        result is True
                        or (hasattr(result, 'CONSTRUCTOR_ID'))  # Any TLObject = accepted
                        or getattr(result, 'accepted', False)
                    )

                    if success or result:
                        print(
                            f" [{Fore.GREEN}✅{Fore.RESET}] Reported!"
                            f" Ac:{Fore.YELLOW}{user_name}{Fore.RESET}"
                            f" Count:{Fore.LIGHTBLUE_EX}{i+1}/{report_count}{Fore.RESET}"
                        )
                    else:
                        print(
                            f" [{Fore.RED}!{Fore.RESET}] Failed!"
                            f" Ac:{Fore.YELLOW}{user_name}{Fore.RESET}"
                            f" Count:{Fore.LIGHTBLUE_EX}{i+1}{Fore.RESET}"
                        )

                except Exception as e:
                    print(
                        f" [{Fore.RED}!{Fore.RESET}] Error at count {i+1}:"
                        f" {Fore.RED}{e}{Fore.RESET}"
                    )
                    await asyncio.sleep(2)  # Rate limit se bachao

    async def run_all_accounts():
        tasks = []
        for sf in session_files:
            # 'Ac1.session' → 'sessions/Ac1'
            session_path = f"sessions/{sf[:-8]}"  # .session (8 chars) remove
            client = TelegramClient(session_path, api_id, api_hash)
            tasks.append(report_channel(client, sf))
        if tasks:
            await asyncio.gather(*tasks)
        else:
            print(f' [{Fore.RED}!{Fore.RESET}] Koi valid session nahi mili!')

    asyncio.run(run_all_accounts())

# ─── Missing args warning ──────────────────────────────────────────────────────
elif (
    command_line_args.add_number is None
    and command_line_args.run is not None
    and (command_line_args.target is None or command_line_args.mode is None)
):
    print(
        f" [{Fore.RED}!{Fore.RESET}] Sahi format use karo{Fore.RED}~>{Fore.RESET}"
        f" python3 {argv[0]} -r 10000 -t channelName -m reportReason"
    )

# ─── Default Banner ───────────────────────────────────────────────────────────
elif (
    command_line_args.add_number is None
    and command_line_args.run is None
    and command_line_args.target is None
    and command_line_args.mode is None
):
    print(f"""
    _____    _ __    t.me/{Fore.MAGENTA}Mr3rf1{Fore.RESET}    💀
   |_   _|__| |  _ \ ___ _ __   ___ _ __
     | |/ _ \ | |_) / _ \ '_ \ / _ \ '__|
     | |  __/ |  _ <  __/ |_) |  __/ |
     |_|\\___|_|_| \\_\\___| .__/ \\___|_|
                         |_|
     github.com/e811-py
{Fore.YELLOW}-----------------------------------------------{Fore.RESET}
 a tool for reporting telegram channels by @Mr3rf1
 use --help to see help: python3 {argv[0]} --help
    """)
