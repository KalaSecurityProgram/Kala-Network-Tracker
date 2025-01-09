import psutil
import time
import os
import platform
import subprocess
import shutil
import requests
from bs4 import BeautifulSoup

# ANSI color codes for styling
GREEN = "\033[92m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

# ASCII Art Banner
BANNER = f"""
{CYAN}{BOLD}
   ██████╗██╗   ██╗██╗      █████╗ ███████╗███████╗
  ██╔════╝██║   ██║██║     ██╔══██╗██╔════╝██╔════╝
  ██║     ██║   ██║██║     ███████║███████╗█████╗  
  ██║     ██║   ██║██║     ██╔══██║╚════██║██╔══╝  
  ╚██████╗╚██████╔╝███████╗██║  ██║███████║███████╗
   ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝
{MAGENTA}
    🌌 Cyberpunk Network Tracker 🌌

    Author: Kala Security Program
    Main Programmer and CEO: N V R K SAI KAMESH YADAVALLI
    Team Manager: Deepya
{YELLOW}
    MIT License
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction.
{RESET}
"""

CURRENT_OS = platform.system()

# Dependency Check
def check_and_install_dependencies():
    """Check and install necessary dependencies."""
    print(f"{CYAN}Checking dependencies...{RESET}")
    if CURRENT_OS == "Linux" and not shutil.which("iptables"):
        print(f"{YELLOW}iptables not found. Installing...{RESET}")
        subprocess.run(["sudo", "apt-get", "install", "-y", "iptables"])
    elif CURRENT_OS == "Darwin" and not shutil.which("pfctl"):
        print(f"{RED}pfctl not found. Ensure macOS Packet Filter is enabled.{RESET}")
    elif CURRENT_OS == "Windows" and not shutil.which("netsh"):
        print(f"{RED}netsh not found. Ensure Windows Firewall is enabled.{RESET}")
    if not shutil.which("nmap"):
        print(f"{YELLOW}nmap not found. Installing...{RESET}")
        if CURRENT_OS == "Linux":
            subprocess.run(["sudo", "apt-get", "install", "-y", "nmap"])
        elif CURRENT_OS == "Darwin":
            subprocess.run(["brew", "install", "nmap"])
        else:
            print(f"{RED}Please download and install nmap manually: https://nmap.org/download.html{RESET}")

# Function to fetch network connections
def get_network_connections():
    """Fetch active network connections."""
    connections = []
    for conn in psutil.net_connections(kind="inet"):
        if conn.laddr and conn.raddr:
            connections.append({
                "local": f"{conn.laddr.ip}:{conn.laddr.port}",
                "remote": f"{conn.raddr.ip}:{conn.raddr.port}",
                "status": conn.status
            })
    return connections

# Function to display connections
def display_connections(connections):
    """Display network connections with cyberpunk styling."""
    os.system("clear" if CURRENT_OS != "Windows" else "cls")
    print(BANNER)
    print(f"{MAGENTA}{'-'*50}{RESET}")
    print(f"{BOLD}No  {GREEN}Local Address          {MAGENTA}Remote Address          {YELLOW}Status{RESET}")
    print(f"{MAGENTA}{'-'*50}{RESET}")
    for index, conn in enumerate(connections, start=1):
        print(f"{index:<3} {GREEN}{conn['local']:<25}{MAGENTA}{conn['remote']:<25}{YELLOW}{conn['status']}{RESET}")
    print(f"{MAGENTA}{'-'*50}{RESET}")

# Function to block a connection
def block_connection(remote_ip):
    """Block a connection based on the OS."""
    try:
        if CURRENT_OS == "Linux":
            subprocess.run(["sudo", "iptables", "-A", "OUTPUT", "-d", remote_ip, "-j", "DROP"])
            subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", remote_ip, "-j", "DROP"])
            print(f"{GREEN}Connection to {remote_ip} blocked successfully on Linux!{RESET}")
        elif CURRENT_OS == "Darwin":
            rule = f"block drop from {remote_ip} to any"
            with open("/etc/pf.conf", "a") as pf_conf:
                pf_conf.write(f"\n{rule}\n")
            subprocess.run(["sudo", "pfctl", "-f", "/etc/pf.conf"])
            print(f"{GREEN}Connection to {remote_ip} blocked successfully on macOS!{RESET}")
        elif CURRENT_OS == "Windows":
            subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", 
                            f"name=Block_{remote_ip}", "dir=out", "action=block", f"remoteip={remote_ip}"])
            subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", 
                            f"name=Block_{remote_ip}", "dir=in", "action=block", f"remoteip={remote_ip}"])
            print(f"{GREEN}Connection to {remote_ip} blocked successfully on Windows!{RESET}")
        else:
            print(f"{RED}Unsupported OS for blocking: {CURRENT_OS}{RESET}")
    except Exception as e:
        print(f"{RED}Error blocking connection: {str(e)}{RESET}")

# Function to perform an Nmap scan
def nmap_scan(remote_ip):
    """Perform an Nmap scan and handle services."""
    print(f"{CYAN}Running Nmap scan on {remote_ip}...{RESET}")
    try:
        result = subprocess.run(["nmap", "-Pn", "-sV", remote_ip], capture_output=True, text=True)
        print(f"{MAGENTA}{'-'*50}{RESET}")
        print(f"{GREEN}{result.stdout}{RESET}")
        print(f"{MAGENTA}{'-'*50}{RESET}")

        # Parse Nmap results for service-specific actions
        if "ssh" in result.stdout.lower():
            print(f"{CYAN}SSH service detected on {remote_ip}. Block this service? (y/n){RESET}")
            choice = input("> ").strip().lower()
            if choice == "y":
                block_connection(remote_ip)
        elif "http" in result.stdout.lower():
            print(f"{CYAN}HTTP/HTTPS service detected. Fetch and analyze content? (y/n){RESET}")
            choice = input("> ").strip().lower()
            if choice == "y":
                fetch_service_content(remote_ip)
        else:
            print(f"{YELLOW}Other services detected. Do you want to block all traffic to {remote_ip}? (y/n){RESET}")
            choice = input("> ").strip().lower()
            if choice == "y":
                block_connection(remote_ip)

    except FileNotFoundError:
        print(f"{RED}Nmap is not installed. Please install it to use this feature.{RESET}")
    except Exception as e:
        print(f"{RED}Error during Nmap scan: {str(e)}{RESET}")

# Function to fetch and analyze service content
def fetch_service_content(remote_ip):
    """Fetch and analyze HTTP/HTTPS content."""
    try:
        url = f"http://{remote_ip}"
        print(f"{CYAN}Fetching content from {url}...{RESET}")
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            print(f"{GREEN}Content fetched successfully. Analyzing for malicious patterns...{RESET}")

            # Basic analysis for malicious patterns
            keywords = ["phishing", "malware", "login", "password", "credit card"]
            found_keywords = [kw for kw in keywords if kw in response.text.lower()]
            scripts = soup.find_all("script")

            print(f"{YELLOW}Keywords Found: {found_keywords if found_keywords else 'None'}{RESET}")
            print(f"{MAGENTA}Number of <script> tags: {len(scripts)}{RESET}")

            if found_keywords or len(scripts) > 5:
                print(f"{RED}Warning: This service might be malicious! Proceed with caution.{RESET}")
            else:
                print(f"{GREEN}No obvious malicious patterns detected.{RESET}")

        else:
            print(f"{RED}Failed to fetch content. HTTP Status Code: {response.status_code}{RESET}")

    except requests.exceptions.RequestException as e:
        print(f"{RED}Error fetching content: {str(e)}{RESET}")

# Main tracker
def run_tracker():
    """Run the real-time network tracker."""
    check_and_install_dependencies()
    try:
        while True:
            connections = get_network_connections()
            display_connections(connections)

            print(f"{CYAN}Options:{RESET}")
            print(f"{GREEN}1. Block an established connection{RESET}")
            print(f"{MAGENTA}2. Run an advanced Nmap scan{RESET}")
            print(f"{YELLOW}Press Enter to refresh the tracker.{RESET}")

            choice = input("> ").strip()
            if choice == "1":
                serial = int(input(f"{CYAN}Enter the serial number of the connection to block: {RESET}").strip())
                conn = connections[serial - 1]
                if conn["status"] == "ESTABLISHED":
                    remote_ip = conn["remote"].split(":")[0]
                    block_connection(remote_ip)
                else:
                    print(f"{YELLOW}Only ESTABLISHED connections can be blocked.{RESET}")
            elif choice == "2":
                serial = int(input(f"{MAGENTA}Enter the serial number for Nmap scan: {RESET}").strip())
                conn = connections[serial - 1]
                remote_ip = conn["remote"].split(":")[0]
                nmap_scan(remote_ip)
            elif choice == "":
                continue
            else:
                print(f"{YELLOW}Invalid option. Try again.{RESET}")

            print(f"\n{CYAN}Press Enter to refresh the connections list.{RESET}")
            input("> ")

    except KeyboardInterrupt:
        print(f"{CYAN}Exiting Cyberpunk Tracker. Stay safe!{RESET}")


if __name__ == "__main__":
    run_tracker()
