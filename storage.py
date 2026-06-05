import json
import os

FILE = "domains.json"


def load_domains():
    if not os.path.exists(FILE):
        return []

    with open(FILE, "r") as f:
        return json.load(f)


def save_domains(domains):
    with open(FILE, "w") as f:
        json.dump(domains, f, indent=2)


def add_domain(domain):
    domains = load_domains()

    domain = domain.lower().strip()

    if domain in [d.lower() for d in domains]:
        return False

    domains.append(domain)

    save_domains(domains)

    return True


def delete_domain(domain):
    domains = load_domains()

    domains = [
        d for d in domains
        if d.lower() != domain.lower()
    ]

    save_domains(domains)


def replace_domain(old_domain, new_domain):
    domains = load_domains()

    domains = [
        new_domain if d.lower() == old_domain.lower()
        else d
        for d in domains
    ]

    save_domains(domains)


# ==================================
# TAMBAHKAN BAGIAN INI DI BAWAH
# ==================================

WEB_STATUS_FILE = "webstatus.json"


def save_web_status(data):

    with open(
        WEB_STATUS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )