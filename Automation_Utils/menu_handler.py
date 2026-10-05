import threading
import sys

BACK = "__BACK__"
EXIT = "__EXIT__"


# =========================
# INPUT DENGAN TIMEOUT
# =========================
def input_with_timeout(prompt="", timeout=30):
    user_input = [None]

    def _get_input():
        try:
            user_input[0] = input(prompt)
        except:
            user_input[0] = None

    thread = threading.Thread(target=_get_input)
    thread.daemon = True
    thread.start()

    thread.join(timeout)

    # 🔥 JANGAN sys.exit()
    if thread.is_alive():
        print(f"\n⏰ Tidak ada aktivitas selama {timeout} detik.")
        return EXIT

    return user_input[0]


# =========================
# SAFE INPUT (GLOBAL)
# =========================
def safe_input(prompt="", timeout=30, allow_back=True):
    val = input_with_timeout(prompt, timeout)

    # 🔥 HANDLE TIMEOUT
    if val in [None, EXIT]:
        print("\n⏰ Timeout.")
        return EXIT

    val = val.strip()
    low = val.lower()

    # 🔥 BACK
    if allow_back and low in ["0", "b", "back"]:
        return BACK

    # 🔥 EXIT MANUAL
    if low in ["exit", "q", "quit"]:
        return EXIT

    return val


# =========================
# MENU PILIHAN
# =========================
def pilih_menu(title, options, timeout=30):

    while True:
        print(f"\n===== {title} =====")

        for i, opt in enumerate(options, 1):
            print(f"{i}. {opt}")

        print("0. Kembali")

        choice = safe_input("Pilih: ", timeout)

        # 🔥 HANDLE EXIT
        if choice == EXIT:
            return EXIT

        # 🔥 HANDLE BACK
        if choice == BACK:
            return BACK

        # 🔥 VALIDASI
        if choice.isdigit():
            idx = int(choice)

            if 1 <= idx <= len(options):
                return options[idx - 1]

        print("❌ Input tidak valid. Coba lagi.")
