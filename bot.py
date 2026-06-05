from datetime import datetime, timedelta
from telegram import (
    Update,
    BotCommand
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)


from config import BOT_TOKEN, CHAT_ID
blocked_domains = {}
from nawala import check_domain

from storage import (
    add_domain,
    delete_domain,
    replace_domain,
    load_domains,
    save_web_status
)

async def mulai(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🤖 Nawala Checker Bot\n\n"
        "📌 Commands:\n\n"
        "/add domain.com\n"
        "Tambah domain\n\n"
        "/delete domain.com\n"
        "Hapus domain\n\n"
        "/replace lama.com baru.com\n"
        "Ganti domain\n\n"
        "/list\n"
        "Lihat daftar domain\n\n"
        "/webstatus\n"
        "Lihat status semua domain"
    )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    domain = update.message.text.strip()

    try:
        msg = await update.message.reply_text(
            "🔍 Sedang mengecek..."
        )

        result = check_domain(domain)

        item = result["data"][0]

        nawala_status = (
            "🚫 BLOCKED"
            if item["nawala"]["blocked"]
            else "✅ NOT BLOCKED"
        )

        network_status = (
            "🚫 BLOCKED"
            if item["network"]["blocked"]
            else "✅ NOT BLOCKED"
        )

        text = (
            f"🌐 Domain: {item['domain']}\n\n"
            f"Nawala: {nawala_status}\n"
            f"Network: {network_status}"
        )

        await msg.edit_text(text)

    except Exception as e:
        await update.message.reply_text(
            f"Error:\n{e}"
        )

async def add(update, context):

    if not context.args:
        return await update.message.reply_text(
            "Contoh:\n/add google.com"
        )

    domain = context.args[0].strip().lower()

    domains = load_domains()

    if domain in [d.lower() for d in domains]:
        return await update.message.reply_text(
            f"⚠️ Domain sudah ada\n\n{domain}"
        )

    add_domain(domain)

    result = check_domain(domain)

    if not result.get("data"):
        return await update.message.reply_text(
            f"✅ Domain ditambahkan\n\n{domain}\n\n"
            f"Namun API tidak mengembalikan data."
        )

    item = result["data"][0]

    nawala = (
        "🚫 BLOCKED"
        if item["nawala"]["blocked"]
        else "✅ NOT BLOCKED"
    )

    network = (
        "🚫 BLOCKED"
        if item["network"]["blocked"]
        else "✅ NOT BLOCKED"
    )

    await update.message.reply_text(
        f"✅ Domain ditambahkan\n\n"
        f"🌐 {item['domain']}\n"
        f"Nawala: {nawala}\n"
        f"Network: {network}"
    )


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        return

    domain = context.args[0].lower()

    delete_domain(domain)

    blocked_domains.pop(
        domain,
        None
    )

    await update.message.reply_text(
        "✅ Domain dihapus"
    )


async def replace(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) < 2:
        return await update.message.reply_text(
            "/replace lama.com baru.com"
        )

    old_domain = context.args[0].lower()
    new_domain = context.args[1].lower()

    domains = load_domains()

    if new_domain in [d.lower() for d in domains]:
        return await update.message.reply_text(
            "⚠️ Domain tujuan sudah ada."
        )

    replace_domain(
        old_domain,
        new_domain
    )

    blocked_domains.pop(
        old_domain,
        None
    )

    await update.message.reply_text(
        f"✅ Replace\n\n"
        f"{old_domain}\n→\n{new_domain}"
    )


async def list_domains(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    domains = load_domains()

    if not domains:
        return await update.message.reply_text(
            "Belum ada domain."
        )

    text = "📊 STATUS DOMAIN\n\n"

    for i, domain in enumerate(domains, mulai=1):

        try:

            result = check_domain(domain)

            data = result.get("data", [])

            if not data:

                status = "⚪ UNKNOWN"

            else:

                item = data[0]

                blocked = (
                    item["nawala"]["blocked"]
                    or
                    item["network"]["blocked"]
                )

                status = (
                    "🚫 BLOCKED"
                    if blocked
                    else "🟢 NOT BLOCKED"
                )

            text += (
                f"{i}. {domain}\n"
                f"{status}\n\n"
            )

        except Exception:

            text += (
                f"{i}. {domain}\n"
                f"❌ ERROR\n\n"
            )

    await update.message.reply_text(text)


async def webstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):

    domains = load_domains()

    if not domains:
        return await update.message.reply_text(
            "Belum ada domain."
        )

    result_text = ""

    for domain in domains:

        try:

            result = check_domain(domain)

            item = result["data"][0]

            nawala = (
                "🚫 BLOCKED"
                if item["nawala"]["blocked"]
                else "✅ NOT BLOCKED"
            )

            network = (
                "🚫 BLOCKED"
                if item["network"]["blocked"]
                else "✅ NOT BLOCKED"
            )

            result_text += (
                f"🌐 {domain}\n"
                f"Nawala: {nawala}\n"
                f"Network: {network}\n\n"
            )

        except Exception:
            result_text += (
                f"🌐 {domain}\n"
                f"❌ ERROR\n\n"
            )

    await update.message.reply_text(result_text)

async def monitor_domains(
    context: ContextTypes.DEFAULT_TYPE
):

    domains = load_domains()

    print(
        f"[MONITOR] checking {len(domains)} domains"
    )

    status_list = []

    for domain in domains:

        try:

            result = check_domain(domain)

            data = result.get("data", [])

            if not data:
                continue

            item = data[0]

            nawala_blocked = item["nawala"]["blocked"]
            network_blocked = item["network"]["blocked"]

            blocked = (
                nawala_blocked
                or
                network_blocked
            )

            status_list.append({
                "domain": domain,
                "nawala": nawala_blocked,
                "network": network_blocked,
                "checked_at": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            })

            if blocked:

                if domain not in blocked_domains:

                    blocked_domains[domain] = True

                    await context.bot.send_message(
                        chat_id=CHAT_ID,
                        text=(
                            "🚨 DOMAIN TERDETEKSI BLOCKED\n\n"
                            f"🌐 {domain}\n\n"
                            "SEGERA GANTI KO!"
                        )
                    )

            else:

                if domain in blocked_domains:

                    del blocked_domains[domain]

                    await context.bot.send_message(
                        chat_id=CHAT_ID,
                        text=(
                            "✅ DOMAIN KEMBALI NORMAL\n\n"
                            f"🌐 {domain}"
                        )
                    )

        except Exception as e:

            print(
                "MONITOR ERROR:",
                e
            )

    save_web_status({

        "last_update":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "next_update":
            (
                datetime.now()
                + timedelta(minutes=5)
            ).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "domains":
            status_list
    })

    domains = load_domains()

    print(
        f"[MONITOR] checking {len(domains)} domains"
    )

    for domain in domains:

        try:

            result = check_domain(domain)

            data = result.get("data", [])

            if not data:
                continue

            item = data[0]

            blocked = (
                item["nawala"]["blocked"]
                or
                item["network"]["blocked"]
            )

            if blocked:

                if domain not in blocked_domains:

                    blocked_domains[domain] = True

                    await context.bot.send_message(
                        chat_id=CHAT_ID,
                        text=(
                            "🚨 DOMAIN TERDETEKSI BLOCKED\n\n"
                            f"🌐 {domain}\n\n"
                            "SEGERA GANTI KO!"
                        )
                    )

            else:

                if domain in blocked_domains:

                    del blocked_domains[domain]

                    await context.bot.send_message(
                        chat_id=CHAT_ID,
                        text=(
                            "✅ DOMAIN KEMBALI NORMAL\n\n"
                            f"🌐 {domain}"
                        )
                    )

        except Exception as e:

            print("MONITOR ERROR:", e)

async def alert_blocked(
    context: ContextTypes.DEFAULT_TYPE
):

    print(
        f"[ALERT] blocked={len(blocked_domains)}"
    )

    if not blocked_domains:
        return

    for domain in list(blocked_domains.keys()):

        domains = load_domains()

        if domain not in domains:

            del blocked_domains[domain]
            continue

        try:

            result = check_domain(domain)

            data = result.get("data", [])

            if not data:
                continue

            item = data[0]

            blocked = (
                item["nawala"]["blocked"]
                or
                item["network"]["blocked"]
            )

            if not blocked:

                del blocked_domains[domain]

                await context.bot.send_message(
                    chat_id=CHAT_ID,
                    text=(
                        f"✅ DOMAIN NORMAL\n\n{domain}"
                    )
                )

                continue

            await context.bot.send_message(
                chat_id=CHAT_ID,
                text=(
                    "🚨 REMINDER BLOCKED\n\n"
                    f"🌐 {domain}\n\n"
                    "CEPAT GANTI KO!"
                )
            )

        except Exception as e:

            print("ALERT ERROR:", e)

def main():

    app = Application.builder() \
        .token(BOT_TOKEN) \
        .build()

    app.add_handler(
        CommandHandler(
            "mulai",
            mulai
        )
    )

    app.add_handler(
        CommandHandler(
            "add",
            add
        )
    )

    app.add_handler(
        CommandHandler(
            "delete",
            delete
        )
    )

    app.add_handler(
        CommandHandler(
            "replace",
            replace
        )
    )

    app.add_handler(
        CommandHandler(
            "list",
            list_domains
        )
    )

    app.add_handler(
        CommandHandler(
            "webstatus",
            webstatus
        )
    )

    app.add_handler(
        CommandHandler(
            "cek",
            check
        )
    )

    print("CHAT_ID =", CHAT_ID)

    app.job_queue.run_repeating(
        monitor_domains,
        interval=300,
        first=10
    )

    app.job_queue.run_repeating(
        alert_blocked,
        interval=120,
        first=30
    )

    print("Bot running...")

    app.run_polling()


if __name__ == "__main__":
    main()