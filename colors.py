from colorama import Fore, Back, Style, init

# auto-reset so colors don't bleed into the next line
init(autoreset=True)

print(Fore.GREEN + "[OK] System initialized")
print(Fore.YELLOW + "[WARN] Camera not connected")
print(Fore.RED + "[ERROR] API key not found")
print(Fore.CYAN + Style.BRIGHT + "JARVIS> Ready for commands")
print(Style.DIM + "Listening...")