#!/usr/bin/python3
import requests
import time
import os
import sys
import shutil
import threading
import zipfile
from threading import Thread
from queue import Queue

# Enhanced Color Scheme
C_RESET   = "\033[0m"
C_BOLD    = "\033[1m"
C_DIM     = "\033[2m"
C_UNDER   = "\033[4m"
C_ORANGE  = "\033[38;5;208m"
C_PURPLE  = "\033[38;5;93m"
C_GOLD    = "\033[38;5;220m"
C_SILVER  = "\033[38;5;250m"
C_CYAN    = "\033[38;5;51m"
C_GREEN   = "\033[38;5;46m"
C_RED     = "\033[38;5;196m"
C_BLUE    = "\033[38;5;27m"

# Terminal width detection
TERM_WIDTH = shutil.get_terminal_size().columns

# Fancy Banner with LinkedIn
banner = f"""
{C_BOLD}{C_ORANGE}╔{'═' * (TERM_WIDTH - 2)}╗
║{C_RESET}{C_GOLD}{'SubDomain Grabber v1.0'.center(TERM_WIDTH - 2)}{C_ORANGE}║
║{C_RESET}{C_SILVER}{'Created by Muhammad Waseem'.center(TERM_WIDTH - 2)}{C_ORANGE}║
║{C_RESET}{C_SILVER}{'LinkedIn: www.linkedin.com/in/muhammadwaseem11'.center(TERM_WIDTH - 2)}{C_ORANGE}║
║{C_RESET}{C_DIM}{'Powered by Chaos ProjectDiscovery'.center(TERM_WIDTH - 2)}{C_ORANGE}║
║{C_RESET}{C_PURPLE}{'https://chaos.projectdiscovery.io/'.center(TERM_WIDTH - 2)}{C_ORANGE}║
╚{'═' * (TERM_WIDTH - 2)}╝{C_RESET}
"""

# Global settings
USE_COLORS = True
stop_progress = threading.Event()

# Welcome animation
def welcome_screen():
    os.system('clear')
    print(banner)
    print(f"{C_CYAN}Initializing Bug Bounty Platform...{C_RESET}")
    for i in range(5):
        sys.stdout.write(f"\r{C_GOLD}Loading [{'█' * (i + 1)}{' ' * (4 - i)}]{C_RESET}")
        sys.stdout.flush()
        time.sleep(0.3)
    print(f"\n{C_GREEN}[✓] Platform ready!{C_RESET}")
    time.sleep(1)
    os.system('clear')

# Progress bar for downloads
def progress_bar(total, completed):
    bar_length = 20
    percent = (completed / total) * 100
    filled = int(bar_length * completed // total)
    bar = '█' * filled + ' ' * (bar_length - filled)
    sys.stdout.write(f"\r{C_CYAN}[{bar}] {percent:.1f}% ({completed}/{total}){C_RESET}")
    sys.stdout.flush()

def fetch_data():
    try:
        url = "https://chaos-data.projectdiscovery.io/index.json"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"{C_RED}[-] Error fetching data: {e}{C_RESET}")
        sys.exit(1)

def display_stats():
    data = fetch_data()
    stats = {
        'new': 0, 'hackerone': 0, 'bugcrowd': 0, 'intigriti': 0, 'external': 0,
        'changed': 0, 'subdomains': 0, 'rewards': 0, 'norewards': 0, 'swags': 0
    }

    for item in data:
        stats['new'] += 1 if item['is_new'] else 0
        stats['hackerone'] += 1 if item['platform'] == "hackerone" else 0
        stats['bugcrowd'] += 1 if item['platform'] == "bugcrowd" else 0
        stats['intigriti'] += 1 if "intigriti" in item['program_url'] else 0
        stats['external'] += 1 if item['platform'] == "" else 0
        stats['changed'] += 1 if item['change'] != 0 else 0
        stats['subdomains'] += item['count']
        stats['rewards'] += 1 if item['bounty'] else 0
        stats['norewards'] += 1 if not item['bounty'] else 0
        stats['swags'] += 1 if 'swag' in item else 0

    subdomains_str = f"{stats['subdomains']:,}"
    subdomains_formatted = f"{subdomains_str:<30}"

    stats_box = [
        f"{C_SILVER if USE_COLORS else ''}╔{'═' * 42}╗",
        f"║{C_BOLD}{C_GOLD if USE_COLORS else ''} Statistics{' ':<31}{C_RESET}{C_SILVER if USE_COLORS else ''}║",
        f"╠{'═' * 42}╣",
        f"║ {C_CYAN if USE_COLORS else ''}Last Updated:{C_RESET} {data[0]['last_updated'][:10]:<28}{C_SILVER if USE_COLORS else ''}║",
        f"║ {C_CYAN if USE_COLORS else ''}Subdomains:{C_RESET} {subdomains_formatted}{C_SILVER if USE_COLORS else ''}║",
        f"║ {C_CYAN if USE_COLORS else ''}Programs:{C_RESET} {len(data):<32}{C_SILVER if USE_COLORS else ''}║",
        f"╠{'─' * 42}╣",
        f"║ {C_GOLD if USE_COLORS else ''}New:{C_RESET} {stats['new']:<9} {C_GOLD if USE_COLORS else ''}Updated:{C_RESET} {stats['changed']:<20}{C_SILVER if USE_COLORS else ''}║",
        f"║ {C_PURPLE if USE_COLORS else ''}H1:{C_RESET} {stats['hackerone']:<10} {C_PURPLE if USE_COLORS else ''}BC:{C_RESET} {stats['bugcrowd']:<10} {C_PURPLE if USE_COLORS else ''}Int:{C_RESET} {stats['intigriti']:<9}{C_SILVER if USE_COLORS else ''}║",
        f"║ {C_ORANGE if USE_COLORS else ''}Ext:{C_RESET} {stats['external']:<9} {C_ORANGE if USE_COLORS else ''}Rewards:{C_RESET} {stats['rewards']:<8} {C_ORANGE if USE_COLORS else ''}Swags:{C_RESET} {stats['swags']:<6}{C_SILVER if USE_COLORS else ''}║",
        f"╚{'═' * 42}╝{C_RESET}"
    ]
    print('\n'.join(stats_box) + '\n')

def get_user_choice(prompt, valid_options):
    while True:
        choice = input(f"{C_CYAN if USE_COLORS else ''}{prompt}{C_RESET}").strip().lower()
        if choice in valid_options:
            return choice
        print(f"{C_RED if USE_COLORS else ''}[-] Invalid option. Please try again.{C_RESET}")

def display_menu():
    menu = [
        f"{C_GOLD if USE_COLORS else ''}1. View Stats{C_RESET}",
        f"{C_GOLD if USE_COLORS else ''}2. List Programs{C_RESET}",
        f"{C_GOLD if USE_COLORS else ''}3. Download Subdomains{C_RESET}",
        f"{C_GOLD if USE_COLORS else ''}4. Exit{C_RESET}"
    ]
    print(f"{C_SILVER if USE_COLORS else ''}╔{'═' * 42}╗")
    print(f"║{C_BOLD}{C_PURPLE if USE_COLORS else ''} Bug Bounty Subdomain Platform{' ':<12}{C_RESET}{C_SILVER if USE_COLORS else ''}║")
    print(f"╠{'═' * 42}╣")
    for option in menu:
        print(f"║ {option:<40}{C_SILVER if USE_COLORS else ''}║")
    print(f"╚{'═' * 42}╝{C_RESET}\n")

def display_filters():
    filters = [
        f"{C_GOLD if USE_COLORS else ''}1. All Programs{C_RESET}",
        f"{C_GOLD if USE_COLORS else ''}2. BugCrowd{C_RESET}",
        f"{C_GOLD if USE_COLORS else ''}3. HackerOne{C_RESET}",
        f"{C_GOLD if USE_COLORS else ''}4. Intigriti{C_RESET}",
        f"{C_GOLD if USE_COLORS else ''}5. External (Self-Hosted){C_RESET}",
        f"{C_GOLD if USE_COLORS else ''}6. Programs with Swags{C_RESET}",
        f"{C_GOLD if USE_COLORS else ''}7. Programs with Rewards{C_RESET}",
        f"{C_GOLD if USE_COLORS else ''}8. Programs without Rewards{C_RESET}",
        f"{C_GOLD if USE_COLORS else ''}9. New Programs{C_RESET}",
        f"{C_GOLD if USE_COLORS else ''}10. Updated Programs{C_RESET}",
        f"{C_GOLD if USE_COLORS else ''}11. Search by Name{C_RESET}"
    ]
    print(f"{C_SILVER if USE_COLORS else ''}╔{'═' * 42}╗")
    print(f"║{C_BOLD}{C_PURPLE if USE_COLORS else ''} Select Filter{' ':<28}{C_RESET}{C_SILVER if USE_COLORS else ''}║")
    print(f"╠{'═' * 42}╣")
    for f in filters:
        print(f"║ {f:<40}{C_SILVER if USE_COLORS else ''}║")
    print(f"╚{'═' * 42}╝{C_RESET}\n")

def list_programs(filter_func=None, color=C_SILVER, title="Programs"):
    data = fetch_data()
    filtered = [item for item in data if not filter_func or filter_func(item)]
    if not filtered:
        print(f"{C_RED if USE_COLORS else ''}[-] No programs match criteria{C_RESET}")
        return

    sort_options = {
        '1': lambda x: x['name'].lower(),  # Name ascending
        '2': lambda x: -x['count'],        # Subdomains descending
        '3': lambda x: x['last_updated']   # Last updated descending
    }
    sort_prompt = "Sort by: (1) Name (asc), (2) Subdomains (desc), (3) Last Updated (desc) [1-3]: "
    sort_choice = get_user_choice(sort_prompt, ['1', '2', '3'])
    filtered.sort(key=sort_options[sort_choice], reverse=(sort_choice != '1'))

    page_size = 10
    total_pages = (len(filtered) + page_size - 1) // page_size
    page = 1

    while True:
        start = (page - 1) * page_size
        end = min(start + page_size, len(filtered))
        print(f"{C_PURPLE if USE_COLORS else ''}{C_UNDER}{title:^74}{C_RESET}")
        print(f"{C_SILVER if USE_COLORS else ''}├{'─' * 72}┤{C_RESET}")
        for i, item in enumerate(filtered[start:end], start + 1):
            name = item['name'][:30] if len(item['name']) > 30 else item['name']
            subdomains = f"{item['count']:,}"
            updated = item['last_updated'][:10]
            print(f"{color}{i:03d}. {name:<30} | Subdomains: {subdomains:<12} | Last Updated: {updated}{C_RESET}")
        print(f"{C_SILVER if USE_COLORS else ''}└{'─' * 72}┘{C_RESET}")
        print(f"{C_CYAN if USE_COLORS else ''}Page {page}/{total_pages} - (N)ext, (P)rev, (Q)uit: {C_RESET}", end='')
        nav = get_user_choice("", ['n', 'p', 'q'])
        if nav == 'q':
            break
        elif nav == 'n' and page < total_pages:
            page += 1
        elif nav == 'p' and page > 1:
            page -= 1

def sanitize_name(name):
    # Replace spaces and invalid characters with underscores
    return ''.join('_' if c in ' /\\:*?"<>|' else c for c in name)

def process_subdomain_file(program_name, zip_path):
    # Sanitize the program name for directory creation
    dir_name = sanitize_name(program_name)
    os.makedirs(dir_name, exist_ok=True)

    # Unzip the file
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dir_name)
        print(f"{C_GREEN if USE_COLORS else ''}[✓] Unzipped: {program_name} to {dir_name}{C_RESET}")
    except zipfile.BadZipFile:
        print(f"{C_RED if USE_COLORS else ''}[-] Error unzipping {program_name}: Invalid ZIP file{C_RESET}")
        return

    # Find the extracted file (assuming one text file per ZIP)
    extracted_files = [f for f in os.listdir(dir_name) if f.endswith('.txt')]
    if not extracted_files:
        print(f"{C_RED if USE_COLORS else ''}[-] No text file found in {program_name} ZIP{C_RESET}")
        return
    raw_file = os.path.join(dir_name, extracted_files[0])
    os.rename(raw_file, os.path.join(dir_name, 'raw_subdomains.txt'))

    # Clean subdomains (remove stars)
    clean_file = os.path.join(dir_name, 'clean_subdomains.txt')
    with open(os.path.join(dir_name, 'raw_subdomains.txt'), 'r') as raw, open(clean_file, 'w') as clean:
        for line in raw:
            cleaned = line.strip().replace('*.', '')
            if cleaned:
                clean.write(cleaned + '\n')
    print(f"{C_GREEN if USE_COLORS else ''}[✓] Cleaned subdomains saved: {clean_file}{C_RESET}")

    # Remove the ZIP file
    os.remove(zip_path)
    print(f"{C_GREEN if USE_COLORS else ''}[✓] Removed ZIP: {zip_path}{C_RESET}")

def download_and_process_program(program_name):
    for item in fetch_data():
        if item['name'] == program_name:
            print(f"{C_GOLD if USE_COLORS else ''}[+] Found: {program_name:<30}{C_RESET}")
            print(f"{C_CYAN if USE_COLORS else ''}[*] Downloading...{C_RESET}", end='\r')
            try:
                resp = requests.get(item['URL'], timeout=10)
                resp.raise_for_status()
                zip_path = f"{sanitize_name(program_name)}.zip"
                with open(zip_path, 'wb') as f:
                    f.write(resp.content)
                print(f"{C_GREEN if USE_COLORS else ''}[✓] Downloaded: {zip_path}{' ':<20}{C_RESET}")
                process_subdomain_file(program_name, zip_path)
            except requests.RequestException as e:
                print(f"{C_RED if USE_COLORS else ''}[-] Error downloading {program_name}: {e}{C_RESET}")
            return
    print(f"{C_RED if USE_COLORS else ''}[-] Not Found: {program_name:<30}{C_RESET}")

def download_worker(queue, color, total):
    global downloaded_count
    while not queue.empty():
        item = queue.get()
        try:
            print(f"{color}[*] Downloading: {item['name']:<30}{C_RESET}", end='\r')
            resp = requests.get(item['URL'], timeout=10)
            resp.raise_for_status()
            zip_path = f"{sanitize_name(item['name'])}.zip"
            with open(zip_path, 'wb') as f:
                f.write(resp.content)
            with threading.Lock():
                downloaded_count += 1
                progress_bar(total, downloaded_count)
            process_subdomain_file(item['name'], zip_path)
        except requests.RequestException as e:
            print(f"{C_RED if USE_COLORS else ''}[-] Error downloading {item['name']}: {e}{C_RESET}")
        queue.task_done()

def process_programs(filter_func=None, color=C_SILVER, title="Processing Programs"):
    global downloaded_count
    data = fetch_data()
    filtered = [item for item in data if not filter_func or filter_func(item)]
    if not filtered:
        print(f"{C_RED if USE_COLORS else ''}[-] No programs to process{C_RESET}")
        return

    queue = Queue()
    for item in filtered:
        queue.put(item)

    total = len(filtered)
    downloaded_count = 0
    print(f"{C_BLUE if USE_COLORS else ''}{C_UNDER}{title:^74}{C_RESET}")

    threads = []
    for _ in range(min(5, queue.qsize())):
        t = Thread(target=download_worker, args=(queue, color, total))
        t.start()
        threads.append(t)

    queue.join()
    stop_progress.set()
    for t in threads:
        t.join()
    print(f"\n{C_GREEN if USE_COLORS else ''}[✓] Completed: {downloaded_count} programs processed{' ':<10}{C_RESET}")

def interactive_menu():
    welcome_screen()
    while True:
        print(banner)
        display_menu()
        action = get_user_choice("Select an option (1-4): ", [str(i) for i in range(1, 5)])

        if action == '4':
            print(f"{C_GREEN if USE_COLORS else ''}[✓] Goodbye!{C_RESET}")
            break
        elif action == '1':
            display_stats()
        elif action == '2':
            display_filters()
            filter_choice = get_user_choice("Select a filter (1-11): ", [str(i) for i in range(1, 12)])
            filters = {
                '1': (None, C_SILVER, "All Programs"),
                '2': (lambda x: x['platform'] == "bugcrowd", C_GOLD, "BugCrowd Programs"),
                '3': (lambda x: x['platform'] == "hackerone", C_SILVER, "HackerOne Programs"),
                '4': (lambda x: "intigriti" in x['program_url'], C_PURPLE, "Intigriti Programs"),
                '5': (lambda x: x['platform'] == "", C_CYAN, "External Programs"),
                '6': (lambda x: 'swag' in x, C_ORANGE, "Swag Programs"),
                '7': (lambda x: x['bounty'], C_GREEN, "Rewards Programs"),
                '8': (lambda x: not x['bounty'], C_RED, "No Rewards Programs"),
                '9': (lambda x: x['is_new'], C_CYAN, "New Programs"),
                '10': (lambda x: x['change'] != 0, C_SILVER, "Updated Programs"),
                '11': (None, C_SILVER, "Search Results")
            }
            filter_func, color, title = filters[filter_choice]
            if filter_choice == '11':
                search_term = input(f"{C_CYAN if USE_COLORS else ''}Enter program name to search: {C_RESET}").strip().lower()
                filter_func = lambda x: search_term in x['name'].lower()
                title = f"Search Results for '{search_term}'"
            list_programs(filter_func, color, title)
        elif action == '3':
            display_filters()
            filter_choice = get_user_choice("Select a filter (1-11): ", [str(i) for i in range(1, 12)])
            filters = {
                '1': (None, C_SILVER, "Processing All Programs"),
                '2': (lambda x: x['platform'] == "bugcrowd", C_GOLD, "Processing BugCrowd Programs"),
                '3': (lambda x: x['platform'] == "hackerone", C_SILVER, "Processing HackerOne Programs"),
                '4': (lambda x: "intigriti" in x['program_url'], C_PURPLE, "Processing Intigriti Programs"),
                '5': (lambda x: x['platform'] == "", C_CYAN, "Processing External Programs"),
                '6': (lambda x: 'swag' in x, C_ORANGE, "Processing Swag Programs"),
                '7': (lambda x: x['bounty'], C_GREEN, "Processing Rewards Programs"),
                '8': (lambda x: not x['bounty'], C_RED, "Processing No Rewards Programs"),
                '9': (lambda x: x['is_new'], C_CYAN, "Processing New Programs"),
                '10': (lambda x: x['change'] != 0, C_SILVER, "Processing Updated Programs"),
                '11': (None, C_SILVER, "Processing Search Results")
            }
            filter_func, color, title = filters[filter_choice]
            if filter_choice == '11':
                search_term = input(f"{C_CYAN if USE_COLORS else ''}Enter program name to search: {C_RESET}").strip().lower()
                filter_func = lambda x: search_term in x['name'].lower()
                title = f"Processing Search Results for '{search_term}'"
                if len([item for item in fetch_data() if filter_func(item)]) == 1:
                    program_name = next(item['name'] for item in fetch_data() if filter_func(item))
                    download_and_process_program(program_name)
                else:
                    process_programs(filter_func, color, title)
            else:
                process_programs(filter_func, color, title)

        if action != '4':
            get_user_choice("Press Enter to continue...", [''])
            os.system('clear')

def main():
    try:
        interactive_menu()
    except KeyboardInterrupt:
        stop_progress.set()
        print(f"\n{C_RED if USE_COLORS else ''}[-] Operation cancelled by user{C_RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
