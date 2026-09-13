import os
import random
import json
import sqlite3
import re
import discord
from discord import app_commands

# ============================================================
# SNOWY - DISCORD BOT
# PostgreSQL + discord.py
# ============================================================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = 783728416553566317
APPROVAL_CHANNEL_ID = 1547544145927610439
APPROVAL_FILE = "snowy_approvals.json"

approved_guilds = set()
pending_guilds = {}

if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable is missing!")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


# ============================================================
# RANDOM MESSAGE SYSTEM
# ============================================================

last_messages = {}


def random_message(name, messages):
    if len(messages) <= 1:
        return messages[0]

    previous = last_messages.get(name)
    choices = [m for m in messages if m != previous]
    selected = random.choice(choices)
    last_messages[name] = selected
    return selected


# ============================================================
# INTERACTION MESSAGES
# ============================================================

hug_messages = [
    "{user} hugged {target}! 🫂🐾",
    "Awww! {user} gave {target} a hug! 💕",
    "HUG ATTACK!!! 🫂 {user} hugged {target}!",
    "{user} gave {target} a very fluffy hug :3",
    "Fluffy hug incoming! 🐾 {user} hugged {target}!",
    "{user} and {target} just had a wholesome hug moment! 🫂",
    "{user} delivered a premium-quality hug to {target}. 😭💕",
    "THE HUG HAS BEEN DELIVERED 🫂🐾",
]

hug_bot_messages = [
    "AWWW 😭💕",
    "NO WAYYY 😭🫂",
    "hehe :3",
    "YIPPEEEE 🐾💕",
    "I WAS NOT READY FOR THAT 😭",
    "FREE HUGS!!! 🫂",
    "you just made my day :3",
]

hug_self_messages = [
    "{user} hugged themselves 😭",
    "{user} gave themselves a hug. Honestly? Valid. 🫂",
    "Self-hug detected 😭🐾",
    "10/10 self-care, {user} 🫂💕",
    "{user} unlocked the solo hug achievement 😭",
]

kiss_messages = [
    "{user} gave {target} a friendly little kiss! 💕",
    "Awww! {user} gave {target} a tiny kiss :3",
    "{user} just kissed {target}! 🐾💕",
    "CUTE 😭 {user} gave {target} a kiss!",
    "{user} gave {target} a tiny peck! 🐾",
    "A little kiss for {target} from {user}! 💕",
]

kiss_bot_messages = [
    "AYO 😭💕",
    "hehe :3",
    "AWWW 😭",
    "okay that was cute",
    "NOOOO 😭💕",
    "EXCUSE ME?! 😭🐾",
    "I WAS NOT EXPECTING THAT 😭",
]

kiss_self_messages = [
    "{user} kissed themselves 😭",
    "Self-kiss is crazy 💀",
    "{user} really went for the self-kiss 😭",
    "Okay then, {user} :3",
    "Respect the self-love, {user} 💕",
]

cuddle_messages = [
    "{user} cuddled with {target}! 🐾💕",
    "Awww! {user} cuddled {target}! 🫂",
    "CUDDLES!!! {user} + {target} 🐾",
    "{user} and {target} are getting cozy! 💕",
    "{user} cuddled up with {target}! 🧸",
    "COZY MODE ACTIVATED 🐾",
    "Fluffy cuddle time! 🫂🐾",
]

cuddle_bot_messages = [
    "YIPPEE CUDDLES 🐾💕",
    "hehe cozy :3",
    "AWWW 😭",
    "CUDDLE TIME!!! 🫂",
    "COZY!!! 🐾",
    "AWWW YOU'RE SO SWEET 😭💕",
    "okay I'm happy now :3",
]

cuddle_self_messages = [
    "{user} started a solo cuddle session 😭",
    "{user} chose maximum coziness.",
    "Solo cuddle time! 🧸💕",
    "Self-cuddle supremacy 😭🐾",
    "Maximum cozy achieved by {user}. 🐾",
]

pat_messages = [
    "{user} gave {target} some head pats! 🐾",
    "pat pat! {user} patted {target}! :3",
    "Awww, {user} gave {target} head pats! 💕",
    "{user} gave {target} some gentle pats 🐾",
    "HEADPATS!!! {user} → {target} 🐾",
    "{user} decided {target} deserved some pats!",
    "PAT PAT PAT 😭🐾",
]

pat_bot_messages = [
    "PATSSS 🐾💕",
    "hehe thank you :3",
    "MORE 😭",
    "YIPPEE HEADPATS",
    "that was nice 🥺",
    "AWWW 🐾",
    "10/10 pats",
]

pat_self_messages = [
    "{user} patted themselves 😭",
    "Self headpats! 🐾",
    "pat pat yourself, {user} :3",
    "Good job, {user}! 😭💕",
    "Honestly, {user} deserved that pat.",
    "Self-care headpat moment 🐾💕",
]

boop_messages = [
    "{user} booped {target}! 👉🐾",
    "BOOP! {user} got {target}! 👉",
    "{user} gave {target} a nose boop! 🐾",
    "boop :3 {user} → {target}",
    "NOSE BOOP!!! 👉🐾",
    "{user} successfully booped {target} 😭",
    "A tiny boop for {target} from {user}! 👉💕",
]

boop_bot_messages = [
    "BOOP?! 😭",
    "HEY! 😭👉",
    "boop you too :3",
    "HOW DARE YOU 😭",
    "hehe boop",
    "MY NOSE 😭🐾",
    "WHO BOOPED ME?! 😭",
    "BOOP WAR!!!",
]

boop_self_messages = [
    "{user} booped themselves 😭",
    "Self boop! 👉🐾",
    "BOOP YOURSELF :3",
    "{user} really just booped their own nose 😭",
    "That was the most unnecessary boop ever.",
]

highfive_messages = [
    "{user} high-fived {target}! ✋🐾",
    "HIGH FIVE!!! ✋ {user} + {target}",
    "Paw five! 🐾 {user} high-fived {target}!",
    "NICE ONE! {user} high-fived {target}!",
    "{user} gave {target} a high five!",
    "HECK YEAH! ✋🐾",
    "Paw five achieved! {user} + {target} 🐾",
]

highfive_bot_messages = [
    "PAW FIVE!!! 🐾✋",
    "YOOOO ✋😭",
    "NICE!",
    "HECK YEAH 🐾",
    "HIGH FIVE :3",
    "✋🐾 YIPPEE!",
    "10/10 high five 😭",
]

highfive_self_messages = [
    "{user} high-fived themselves 😭✋",
    "Solo high five!",
    "You really high-fived yourself, {user}. 😭",
    "✋ ...there.",
    "Self high-five unlocked ✋🐾",
]

wave_messages = [
    "{user} waved at {target}! 👋🐾",
    "Hiii! {user} waved at {target}! 👋",
    "HEYYYYY! {user} says hi to {target}! 🐾",
    "{user} gave {target} a friendly wave!",
    "WAVE WAVE WAVE!!! 👋🐾",
    "{user} waved at {target}! :3",
    "A wild wave appeared! 👋 {user} → {target}",
]

wave_bot_messages = [
    "HIIIIII 👋🐾",
    "HEYYYYY :3",
    "HIII!!! 😭",
    "YOOOO HI",
    "HELLOOOO 🐾💕",
    "HIIII FREN!!! 👋",
    "YIPPEE HI 🐾",
]

wave_self_messages = [
    "{user} waved at themselves 😭",
    "Hi you! 👋",
    "HELLO THERE, {user} :3",
    "Self-wave!",
    "{user} really just said hi to themselves 😭",
    "👋 Hi, {user}!",
]


# ============================================================
# DATABASE
# ============================================================

db = None


class SQLiteConnection:
    def __init__(self, connection):
        self.connection = connection

    @staticmethod
    def _convert_sql(sql):
        return re.sub(r"\$(\d+)", "?", sql)

    async def execute(self, sql, *args):
        sql = self._convert_sql(sql)
        cur = self.connection.execute(sql, args)
        self.connection.commit()
        command = sql.lstrip().split(None, 1)[0].upper() if sql.strip() else ""
        if command in {"INSERT", "UPDATE", "DELETE", "REPLACE"}:
            return f"{command} {cur.rowcount if cur.rowcount >= 0 else 0}"
        return "OK"

    async def fetchrow(self, sql, *args):
        sql = self._convert_sql(sql)
        cur = self.connection.execute(sql, args)
        row = cur.fetchone()
        return row

    async def fetch(self, sql, *args):
        sql = self._convert_sql(sql)
        cur = self.connection.execute(sql, args)
        return cur.fetchall()


class SQLiteAcquire:
    def __init__(self, connection):
        self.connection = connection
        self.wrapper = SQLiteConnection(connection)

    async def __aenter__(self):
        return self.wrapper

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type:
            self.connection.rollback()
        return False


class SQLitePool:
    def __init__(self, path):
        self.connection = sqlite3.connect(path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

    def acquire(self):
        return SQLiteAcquire(self.connection)

    async def close(self):
        self.connection.close()


async def init_database():
    global db

    db = SQLitePool("snowy.db")

    async with db.acquire() as con:
        await con.execute("""
            CREATE TABLE IF NOT EXISTS guild_config (
                guild_id INTEGER PRIMARY KEY,
                welcome_enabled INTEGER NOT NULL DEFAULT 1,
                welcome_channel INTEGER,
                welcome_title TEXT NOT NULL DEFAULT 'Welcome! 🐾',
                welcome_message TEXT NOT NULL DEFAULT 'Welcome to the furry hangout! 🐾',
                welcome_question TEXT,
                log_channel INTEGER,
                autorole INTEGER
            )
        """)

        await con.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await con.execute("""
            CREATE TABLE IF NOT EXISTS reaction_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                emoji TEXT NOT NULL,
                role_id INTEGER NOT NULL,
                UNIQUE(guild_id, message_id, emoji)
            )
        """)

    print("SQLite connected and tables are ready!")


async def get_config(guild_id):
    async with db.acquire() as con:
        await con.execute("""
            INSERT INTO guild_config (guild_id)
            VALUES ($1)
            ON CONFLICT (guild_id) DO NOTHING
        """, guild_id)

        row = await con.fetchrow("""
            SELECT *
            FROM guild_config
            WHERE guild_id = $1
        """, guild_id)

        return dict(row)


async def log_action(guild, text):
    if not guild:
        return

    config = await get_config(guild.id)
    channel_id = config["log_channel"]

    if not channel_id:
        return

    channel = guild.get_channel(channel_id)

    if channel:
        try:
            await channel.send(text)
        except discord.HTTPException:
            pass


# ============================================================
# BOT
# ============================================================

def save_approval_cache():
    data = {
        "approved_guilds": sorted(approved_guilds),
        "pending_guilds": {str(k): v for k, v in pending_guilds.items()},
    }
    with open(APPROVAL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_approval_cache():
    global approved_guilds, pending_guilds
    try:
        with open(APPROVAL_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        approved_guilds = {int(x) for x in data.get("approved_guilds", [])}
        pending_guilds = {int(k): v for k, v in data.get("pending_guilds", {}).items()}
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        approved_guilds = set()
        pending_guilds = {}


class ServerApprovalView(discord.ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id

        approve = discord.ui.Button(
            label="Approve",
            style=discord.ButtonStyle.success,
            custom_id=f"snowy:approve:{guild_id}",
        )
        deny = discord.ui.Button(
            label="Deny",
            style=discord.ButtonStyle.danger,
            custom_id=f"snowy:deny:{guild_id}",
        )
        approve.callback = self.approve_callback
        deny.callback = self.deny_callback
        self.add_item(approve)
        self.add_item(deny)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                "❌ You're not my creator. Only Kris can approve it.",
                ephemeral=True,
            )
            return False
        return True

    async def approve_callback(self, interaction: discord.Interaction):
        approved_guilds.add(self.guild_id)
        pending_guilds.pop(self.guild_id, None)
        save_approval_cache()

        embed = discord.Embed(
            title="✅ Snowy server approved",
            description=f"Server ID: `{self.guild_id}`\nStatus: `APPROVED`",
            color=discord.Color.green(),
        )
        embed.set_footer(text=f"snowy_approval:approved:{self.guild_id}")

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

    async def deny_callback(self, interaction: discord.Interaction):
        pending_guilds.pop(self.guild_id, None)
        approved_guilds.discard(self.guild_id)
        save_approval_cache()

        guild = bot.get_guild(self.guild_id)
        if guild is not None:
            owner = guild.owner
            if owner is None:
                try:
                    owner = await bot.fetch_user(guild.owner_id)
                except discord.HTTPException:
                    owner = None

            if owner is not None:
                try:
                    await owner.send("sorry but my creator denied your usage access")
                except discord.HTTPException:
                    pass

        embed = discord.Embed(
            title="❌ Snowy server denied",
            description=f"Server ID: `{self.guild_id}`\nStatus: `DENIED`",
            color=discord.Color.red(),
        )
        embed.set_footer(text=f"snowy_approval:denied:{self.guild_id}")

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

        if guild is not None:
            try:
                await guild.leave()
            except discord.HTTPException:
                pass


async def get_approval_channel():
    channel = bot.get_channel(APPROVAL_CHANNEL_ID)
    if channel is None:
        try:
            channel = await bot.fetch_channel(APPROVAL_CHANNEL_ID)
        except discord.HTTPException:
            return None
    return channel


async def sync_approval_channel_database():
    """Use the approval channel as the persistent approval database."""
    channel = await get_approval_channel()
    if channel is None or not hasattr(channel, "history"):
        return

    approved = set()
    pending = {}

    try:
        async for message in channel.history(limit=None):
            if not message.embeds:
                continue
            footer = message.embeds[0].footer.text or ""
            if not footer.startswith("snowy_approval:"):
                continue

            parts = footer.split(":")
            if len(parts) != 3:
                continue

            _, status, guild_id_text = parts
            try:
                guild_id = int(guild_id_text)
            except ValueError:
                continue

            if status == "approved":
                approved.add(guild_id)
                pending.pop(guild_id, None)
            elif status == "pending" and guild_id not in approved:
                pending[guild_id] = {"message_id": message.id}
            elif status == "denied":
                pending.pop(guild_id, None)
                approved.discard(guild_id)
    except discord.HTTPException as exc:
        print(f"Could not read approval channel history: {exc}")
        return

    approved_guilds.clear()
    approved_guilds.update(approved)
    pending_guilds.clear()
    pending_guilds.update(pending)
    save_approval_cache()


async def request_server_approval(guild: discord.Guild):
    if guild.id in approved_guilds:
        return

    if guild.id in pending_guilds:
        return

    try:
        await guild.owner.send(
            "to use this bot you must be given access by the developer of the app please sit tight I've already sent through a request"
        )
    except discord.HTTPException:
        pass

    channel = await get_approval_channel()
    if channel is None:
        print("Approval channel could not be found.")
        return

    embed = discord.Embed(
        title="🐾 Snowy server approval request",
        description=(
            f"Server: **{guild.name}**\n"
            f"Server ID: `{guild.id}`\n"
            f"Owner: {guild.owner.mention if guild.owner else guild.owner_id}\n\n"
            "Snowy is waiting for Kris to approve this server."
        ),
        color=discord.Color.orange(),
    )
    embed.set_footer(text=f"snowy_approval:pending:{guild.id}")

    view = ServerApprovalView(guild.id)
    message = await channel.send(embed=embed, view=view)

    pending_guilds[guild.id] = {"message_id": message.id}
    save_approval_cache()


class Snowy(discord.Client):

    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(
            self,
            allowed_contexts=app_commands.AppCommandContext(
                guild=True,
                dm_channel=False,
                private_channel=False,
            ),
            allowed_installs=app_commands.AppInstallationType(
                guild=True,
                user=True,
            ),
        )

    async def setup_hook(self):
        load_approval_cache()
        await init_database()
        await sync_approval_channel_database()

        for guild_id in pending_guilds:
            self.add_view(ServerApprovalView(guild_id))

        await self.tree.sync()
        print("Slash commands synced!")

    async def on_ready(self):
        print(f"{self.user} successfully started!")
        await self.change_presence(
            activity=discord.Game(name="Furry Hangout | /help")
        )

    async def on_guild_join(self, guild):
        await request_server_approval(guild)


bot = Snowy()


async def approval_gate(interaction: discord.Interaction) -> bool:
    # User-installed apps do not join a guild, so they are not part of the
    # server approval list. They can use Snowy as a user-installed app.
    if interaction.is_user_integration():
        return True

    if interaction.user.id == OWNER_ID:
        return True

    if interaction.guild_id is None:
        return False

    if interaction.guild_id in approved_guilds:
        return True

    if interaction.guild is not None and interaction.guild_id not in pending_guilds:
        await request_server_approval(interaction.guild)

    if interaction.guild_id in pending_guilds:
        raise app_commands.CheckFailure(
            "⏳ Snowy's application for this server is still pending. Please wait for Kris to approve it."
        )

    raise app_commands.CheckFailure(
        "⏳ Snowy hasn't been approved to work in this server yet. Kris needs to approve it first."
    )


bot.tree.interaction_check = approval_gate

# ============================================================
# WELCOME + AUTOROLE
# ============================================================

@bot.event
async def on_member_join(member):
    config = await get_config(member.guild.id)

    # Autorole
    if config["autorole"]:
        role = member.guild.get_role(config["autorole"])

        if role:
            try:
                await member.add_roles(role, reason="Snowy autorole")
            except discord.HTTPException:
                pass

    # Welcome
    if not config["welcome_enabled"] or not config["welcome_channel"]:
        return

    channel = member.guild.get_channel(config["welcome_channel"])

    if not channel:
        return

    default_questions = [
        "Do you already have a fursona? 🐾",
        "What's your favorite animal species? 🦊",
        "Do you like drawing furry art? 🎨",
        "What's your favorite furry character? 🐾",
        "What's your favorite furry game? 🎮🐾",
    ]

    question = config["welcome_question"] or random.choice(default_questions)

    embed = discord.Embed(
        title=config["welcome_title"].replace("{user}", member.name),
        description=(
            f"{config['welcome_message'].replace('{user}', member.mention)}\n\n"
            f"Question for you:\n{question}"
        ),
        color=discord.Color.orange(),
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    try:
        await channel.send(content=member.mention, embed=embed)
    except discord.HTTPException:
        pass


# ============================================================
# INTERACTION HELPER
# ============================================================

async def interaction_command(
    interaction,
    target,
    command_name,
    normal_messages,
    bot_messages,
    self_messages,
):
    if target == bot.user:
        message = random_message(
            f"{command_name}_bot",
            bot_messages,
        )

    elif target == interaction.user:
        messages = [
            x.format(user=interaction.user.mention)
            for x in self_messages
        ]

        message = random_message(
            f"{command_name}_self",
            messages,
        )

    else:
        messages = [
            x.format(
                user=interaction.user.mention,
                target=target.mention,
            )
            for x in normal_messages
        ]

        message = random_message(
            command_name,
            messages,
        )

    await interaction.response.send_message(message)


# ============================================================
# INTERACTIONS
# ============================================================

@bot.tree.command(name="hug", description="Give someone a hug!")
async def hug(interaction: discord.Interaction, tag: discord.User):
    await interaction_command(
        interaction, tag, "hug",
        hug_messages, hug_bot_messages, hug_self_messages
    )


@bot.tree.command(name="kiss", description="Give someone a friendly kiss!")
async def kiss(interaction: discord.Interaction, tag: discord.User):
    await interaction_command(
        interaction, tag, "kiss",
        kiss_messages, kiss_bot_messages, kiss_self_messages
    )


@bot.tree.command(name="cuddle", description="Cuddle with someone!")
async def cuddle(interaction: discord.Interaction, tag: discord.User):
    await interaction_command(
        interaction, tag, "cuddle",
        cuddle_messages, cuddle_bot_messages, cuddle_self_messages
    )


@bot.tree.command(name="pat", description="Give someone head pats!")
async def pat(interaction: discord.Interaction, tag: discord.User):
    await interaction_command(
        interaction, tag, "pat",
        pat_messages, pat_bot_messages, pat_self_messages
    )


@bot.tree.command(name="boop", description="Boop someone's nose!")
async def boop(interaction: discord.Interaction, tag: discord.User):
    await interaction_command(
        interaction, tag, "boop",
        boop_messages, boop_bot_messages, boop_self_messages
    )


@bot.tree.command(name="highfive", description="Give someone a high five!")
async def highfive(interaction: discord.Interaction, tag: discord.User):
    await interaction_command(
        interaction, tag, "highfive",
        highfive_messages, highfive_bot_messages, highfive_self_messages
    )


@bot.tree.command(name="wave", description="Wave at someone!")
async def wave(interaction: discord.Interaction, tag: discord.User):
    await interaction_command(
        interaction, tag, "wave",
        wave_messages, wave_bot_messages, wave_self_messages
    )


# ============================================================
# OWNER-ONLY SAY
# ============================================================

@bot.tree.command(name="say", description="Send a message as Snowy.")
@app_commands.describe(message="The message Snowy should send.")
async def say(interaction: discord.Interaction, message: str):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "❌ You don't have permission to use this command.",
            ephemeral=True,
        )
        return

    # Use the interaction response itself so /say also works when Snowy is
    # installed only to Kris's user account and is not a guild bot member.
    await interaction.response.send_message(message)


# ============================================================
# SERVER INFO
# ============================================================

@bot.tree.command(name="serverinfo", description="Show information about this server.")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild

    embed = discord.Embed(
        title=f"🐾 {guild.name}",
        color=discord.Color.orange(),
    )

    embed.add_field(
        name="Owner",
        value=guild.owner.mention if guild.owner else "Unknown",
    )
    embed.add_field(name="Members", value=str(guild.member_count))
    embed.add_field(name="Channels", value=str(len(guild.channels)))
    embed.add_field(name="Roles", value=str(len(guild.roles)))
    embed.add_field(name="Server ID", value=f"`{guild.id}`")

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    await interaction.response.send_message(embed=embed)


# ============================================================
# USER INFO
# ============================================================

@bot.tree.command(name="userinfo", description="Show information about a member.")
async def userinfo(
    interaction: discord.Interaction,
    member: discord.Member | None = None,
):
    member = member or interaction.user

    embed = discord.Embed(
        title=f"🐾 {member}",
        color=discord.Color.orange(),
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    embed.add_field(name="Username", value=member.name)
    embed.add_field(name="ID", value=f"`{member.id}`")
    embed.add_field(
        name="Joined",
        value=(
            member.joined_at.strftime("%Y-%m-%d")
            if member.joined_at else "Unknown"
        ),
    )

    await interaction.response.send_message(embed=embed)


# ============================================================
# AVATAR
# ============================================================

@bot.tree.command(name="avatar", description="Show someone's avatar.")
async def avatar(
    interaction: discord.Interaction,
    member: discord.Member | None = None,
):
    member = member or interaction.user

    embed = discord.Embed(
        title=f"{member.name}'s Avatar",
        color=discord.Color.orange(),
    )

    embed.set_image(url=member.display_avatar.url)

    await interaction.response.send_message(embed=embed)


# ============================================================
# PING
# ============================================================

@bot.tree.command(name="ping", description="Check Snowy's latency.")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! `{latency}ms`")


# ============================================================
# COINFLIP
# ============================================================

@bot.tree.command(name="coinflip", description="Flip a coin.")
async def coinflip(interaction: discord.Interaction):
    await interaction.response.send_message(
        random.choice(["Heads! 🪙", "Tails! 🪙"])
    )


# ============================================================
# DICE
# ============================================================

@bot.tree.command(name="dice", description="Roll a six-sided dice.")
async def dice(interaction: discord.Interaction):
    result = random.randint(1, 6)
    await interaction.response.send_message(f"🎲 You rolled `{result}`!")


# ============================================================
# CONFIG GROUP
# ============================================================

config_group = app_commands.Group(
    name="config",
    description="Configure Snowy for this server.",
)

bot.tree.add_command(config_group)


@config_group.command(name="view", description="View Snowy's configuration.")
@app_commands.checks.has_permissions(manage_guild=True)
async def config_view(interaction: discord.Interaction):
    config = await get_config(interaction.guild.id)

    welcome_channel = (
        f"<#{config['welcome_channel']}>"
        if config["welcome_channel"] else "Not configured"
    )

    log_channel = (
        f"<#{config['log_channel']}>"
        if config["log_channel"] else "Not configured"
    )

    autorole = (
        f"<@&{config['autorole']}>"
        if config["autorole"] else "Disabled"
    )

    embed = discord.Embed(
        title="⚙️ Snowy Configuration",
        color=discord.Color.orange(),
    )

    embed.add_field(
        name="Welcome",
        value=(
            f"Enabled: `{config['welcome_enabled']}`\n"
            f"Channel: {welcome_channel}\n"
            f"Title: `{config['welcome_title']}`\n"
            f"Message: `{config['welcome_message']}`\n"
            f"Question: `{config['welcome_question'] or 'Random'}`"
        ),
        inline=False,
    )

    embed.add_field(name="Autorole", value=autorole)
    embed.add_field(name="Logs", value=log_channel)

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True,
    )


@config_group.command(name="welcome_channel", description="Set the welcome channel.")
@app_commands.checks.has_permissions(manage_guild=True)
async def welcome_channel(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
):
    await get_config(interaction.guild.id)

    async with db.acquire() as con:
        await con.execute(
            """
            UPDATE guild_config
            SET welcome_channel = $1
            WHERE guild_id = $2
            """,
            channel.id,
            interaction.guild.id,
        )

    await interaction.response.send_message(
        f"👋 Welcome channel set to {channel.mention}."
    )


@config_group.command(name="welcome_toggle", description="Enable or disable welcome messages.")
@app_commands.checks.has_permissions(manage_guild=True)
async def welcome_toggle(
    interaction: discord.Interaction,
    enabled: bool,
):
    await get_config(interaction.guild.id)

    async with db.acquire() as con:
        await con.execute(
            """
            UPDATE guild_config
            SET welcome_enabled = $1
            WHERE guild_id = $2
            """,
            enabled,
            interaction.guild.id,
        )

    await interaction.response.send_message(
        f"👋 Welcome messages are now `{'enabled' if enabled else 'disabled'}`."
    )


@config_group.command(name="welcome_message", description="Set the welcome message.")
@app_commands.checks.has_permissions(manage_guild=True)
async def welcome_message(
    interaction: discord.Interaction,
    message: str,
):
    await get_config(interaction.guild.id)

    async with db.acquire() as con:
        await con.execute(
            """
            UPDATE guild_config
            SET welcome_message = $1
            WHERE guild_id = $2
            """,
            message,
            interaction.guild.id,
        )

    await interaction.response.send_message("✅ Welcome message updated.")


@config_group.command(name="welcome_title", description="Set the welcome embed title.")
@app_commands.checks.has_permissions(manage_guild=True)
async def welcome_title(
    interaction: discord.Interaction,
    title: str,
):
    await get_config(interaction.guild.id)

    async with db.acquire() as con:
        await con.execute(
            """
            UPDATE guild_config
            SET welcome_title = $1
            WHERE guild_id = $2
            """,
            title,
            interaction.guild.id,
        )

    await interaction.response.send_message("✅ Welcome title updated.")


@config_group.command(name="welcome_question", description="Set the welcome question.")
@app_commands.checks.has_permissions(manage_guild=True)
async def welcome_question(
    interaction: discord.Interaction,
    question: str,
):
    await get_config(interaction.guild.id)

    async with db.acquire() as con:
        await con.execute(
            """
            UPDATE guild_config
            SET welcome_question = $1
            WHERE guild_id = $2
            """,
            question,
            interaction.guild.id,
        )

    await interaction.response.send_message("✅ Welcome question updated.")


@config_group.command(name="log_channel", description="Set the moderation log channel.")
@app_commands.checks.has_permissions(manage_guild=True)
async def log_channel(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
):
    await get_config(interaction.guild.id)

    async with db.acquire() as con:
        await con.execute(
            """
            UPDATE guild_config
            SET log_channel = $1
            WHERE guild_id = $2
            """,
            channel.id,
            interaction.guild.id,
        )

    await interaction.response.send_message(
        f"📋 Log channel set to {channel.mention}."
    )


@config_group.command(name="autorole", description="Set the automatic role for new members.")
@app_commands.checks.has_permissions(manage_guild=True)
async def autorole(
    interaction: discord.Interaction,
    role: discord.Role,
):
    await get_config(interaction.guild.id)

    async with db.acquire() as con:
        await con.execute(
            """
            UPDATE guild_config
            SET autorole = $1
            WHERE guild_id = $2
            """,
            role.id,
            interaction.guild.id,
        )

    await interaction.response.send_message(
        f"🎭 Autorole set to {role.mention}."
    )


@config_group.command(name="autorole_off", description="Disable the automatic role.")
@app_commands.checks.has_permissions(manage_guild=True)
async def autorole_off(interaction: discord.Interaction):
    await get_config(interaction.guild.id)

    async with db.acquire() as con:
        await con.execute(
            """
            UPDATE guild_config
            SET autorole = NULL
            WHERE guild_id = $1
            """,
            interaction.guild.id,
        )

    await interaction.response.send_message("🎭 Autorole disabled.")


# ============================================================
# REACTION ROLES
# ============================================================

@config_group.command(name="reactionrole", description="Create a reaction role.")
@app_commands.describe(
    message_id="ID of the message",
    emoji="Emoji for the role",
    role="Role to give",
)
@app_commands.checks.has_permissions(manage_roles=True)
async def reactionrole(
    interaction: discord.Interaction,
    message_id: str,
    emoji: str,
    role: discord.Role,
):
    try:
        message_id_int = int(message_id)
        message = await interaction.channel.fetch_message(message_id_int)
        await message.add_reaction(emoji)
    except (ValueError, discord.NotFound, discord.HTTPException):
        await interaction.response.send_message(
            "❌ I couldn't find that message or use that emoji.",
            ephemeral=True,
        )
        return

    async with db.acquire() as con:
        await con.execute(
            """
            INSERT INTO reaction_roles
                (guild_id, channel_id, message_id, emoji, role_id)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (guild_id, message_id, emoji)
            DO UPDATE SET role_id = EXCLUDED.role_id
            """,
            interaction.guild.id,
            interaction.channel.id,
            message_id_int,
            emoji,
            role.id,
        )

    await interaction.response.send_message(
        f"✅ {emoji} now gives {role.mention}."
    )


@config_group.command(name="reactionrole_remove", description="Remove a reaction role.")
@app_commands.describe(
    message_id="ID of the message",
    emoji="Emoji",
)
@app_commands.checks.has_permissions(manage_roles=True)
async def reactionrole_remove(
    interaction: discord.Interaction,
    message_id: str,
    emoji: str,
):
    try:
        message_id_int = int(message_id)
    except ValueError:
        await interaction.response.send_message(
            "❌ Invalid message ID.",
            ephemeral=True,
        )
        return

    async with db.acquire() as con:
        result = await con.execute(
            """
            DELETE FROM reaction_roles
            WHERE guild_id = $1
            AND message_id = $2
            AND emoji = $3
            """,
            interaction.guild.id,
            message_id_int,
            emoji,
        )

    if result == "DELETE 0":
        await interaction.response.send_message(
            "❌ No reaction role was found.",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            "🗑️ Reaction role removed."
        )


# ============================================================
# REACTION ROLE EVENTS
# ============================================================

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    async with db.acquire() as con:
        row = await con.fetchrow(
            """
            SELECT role_id
            FROM reaction_roles
            WHERE guild_id = $1
            AND message_id = $2
            AND emoji = $3
            """,
            payload.guild_id,
            payload.message_id,
            str(payload.emoji),
        )

    if not row:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id)
    role = guild.get_role(row["role_id"])

    if member and role:
        try:
            await member.add_roles(role, reason="Snowy reaction role")
        except discord.HTTPException:
            pass


@bot.event
async def on_raw_reaction_remove(payload):
    if not payload.guild_id:
        return

    async with db.acquire() as con:
        row = await con.fetchrow(
            """
            SELECT role_id
            FROM reaction_roles
            WHERE guild_id = $1
            AND message_id = $2
            AND emoji = $3
            """,
            payload.guild_id,
            payload.message_id,
            str(payload.emoji),
        )

    if not row:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id)
    role = guild.get_role(row["role_id"])

    if member and role:
        try:
            await member.remove_roles(role, reason="Snowy reaction role")
        except discord.HTTPException:
            pass


# ============================================================
# MODERATION
# ============================================================

async def add_warning(guild_id, user_id, moderator_id, reason):
    async with db.acquire() as con:
        await con.execute(
            """
            INSERT INTO warnings
                (guild_id, user_id, moderator_id, reason)
            VALUES ($1, $2, $3, $4)
            """,
            guild_id,
            user_id,
            moderator_id,
            reason,
        )


async def get_warnings(guild_id, user_id):
    async with db.acquire() as con:
        return await con.fetch(
            """
            SELECT *
            FROM warnings
            WHERE guild_id = $1
            AND user_id = $2
            ORDER BY created_at DESC
            """,
            guild_id,
            user_id,
        )


@bot.tree.command(name="warn", description="Warn a member.")
@app_commands.checks.has_permissions(moderate_members=True)
async def warn(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "No reason provided",
):
    if member == interaction.user:
        await interaction.response.send_message(
            "❌ You can't warn yourself.",
            ephemeral=True,
        )
        return

    await add_warning(
        interaction.guild.id,
        member.id,
        interaction.user.id,
        reason,
    )

    await interaction.response.send_message(
        f"⚠️ {member.mention} has been warned.\nReason: {reason}"
    )

    await log_action(
        interaction.guild,
        f"⚠️ {interaction.user.mention} warned {member.mention}: {reason}",
    )


@bot.tree.command(name="warnings", description="Show a member's warnings.")
@app_commands.checks.has_permissions(moderate_members=True)
async def warnings(
    interaction: discord.Interaction,
    member: discord.Member,
):
    rows = await get_warnings(interaction.guild.id, member.id)

    if not rows:
        await interaction.response.send_message(
            f"✅ {member.mention} has no warnings.",
            ephemeral=True,
        )
        return

    lines = []

    for index, row in enumerate(rows[:10], start=1):
        moderator = interaction.guild.get_member(row["moderator_id"])
        moderator_name = moderator.mention if moderator else f"`{row['moderator_id']}`"

        lines.append(
            f"**{index}.** {row['reason']}\n"
            f"Moderator: {moderator_name}"
        )

    embed = discord.Embed(
        title=f"⚠️ Warnings for {member}",
        description="\n\n".join(lines),
        color=discord.Color.orange(),
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True,
    )


@bot.tree.command(name="clearwarnings", description="Clear all warnings for a member.")
@app_commands.checks.has_permissions(moderate_members=True)
async def clearwarnings(
    interaction: discord.Interaction,
    member: discord.Member,
):
    async with db.acquire() as con:
        result = await con.execute(
            """
            DELETE FROM warnings
            WHERE guild_id = $1
            AND user_id = $2
            """,
            interaction.guild.id,
            member.id,
        )

    await interaction.response.send_message(
        f"🧹 Cleared {result.split()[-1]} warning(s) for {member.mention}."
    )


@bot.tree.command(name="mute", description="Timeout a member.")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(
    interaction: discord.Interaction,
    member: discord.Member,
    minutes: app_commands.Range[int, 1, 40320],
    reason: str = "No reason provided",
):
    if member == interaction.user:
        await interaction.response.send_message(
            "❌ You can't mute yourself.",
            ephemeral=True,
        )
        return

    try:
        await member.timeout(
            discord.utils.utcnow() + discord.timedelta(minutes=minutes),
            reason=reason,
        )
    except AttributeError:
        await member.timeout(
            discord.utils.utcnow() + __import__("datetime").timedelta(minutes=minutes),
            reason=reason,
        )

    await interaction.response.send_message(
        f"🔇 {member.mention} was muted for `{minutes}` minute(s).\nReason: {reason}"
    )

    await log_action(
        interaction.guild,
        f"🔇 {interaction.user.mention} muted {member.mention} for {minutes} minutes: {reason}",
    )


@bot.tree.command(name="unmute", description="Remove a member's timeout.")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(
    interaction: discord.Interaction,
    member: discord.Member,
):
    await member.timeout(None, reason=f"Unmuted by {interaction.user}")

    await interaction.response.send_message(
        f"🔊 {member.mention} has been unmuted."
    )


@bot.tree.command(name="kick", description="Kick a member.")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "No reason provided",
):
    await member.kick(reason=reason)

    await interaction.response.send_message(
        f"👢 {member.mention} was kicked.\nReason: {reason}"
    )

    await log_action(
        interaction.guild,
        f"👢 {interaction.user.mention} kicked {member} ({member.id}): {reason}",
    )


@bot.tree.command(name="ban", description="Ban a member.")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "No reason provided",
):
    await member.ban(reason=reason)

    await interaction.response.send_message(
        f"🔨 {member.mention} was banned.\nReason: {reason}"
    )

    await log_action(
        interaction.guild,
        f"🔨 {interaction.user.mention} banned {member} ({member.id}): {reason}",
    )


@bot.tree.command(name="unban", description="Unban a user by ID.")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(
    interaction: discord.Interaction,
    user_id: str,
):
    try:
        user = await bot.fetch_user(int(user_id))
    except (ValueError, discord.NotFound, discord.HTTPException):
        await interaction.response.send_message(
            "❌ Invalid or unknown user ID.",
            ephemeral=True,
        )
        return

    try:
        await interaction.guild.unban(user)
    except discord.NotFound:
        await interaction.response.send_message(
            "❌ That user is not currently banned.",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(
        f"✅ {user} has been unbanned."
    )


@bot.tree.command(name="clear", description="Delete messages from this channel.")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(
    interaction: discord.Interaction,
    amount: app_commands.Range[int, 1, 100],
):
    await interaction.response.defer(ephemeral=True)

    deleted = await interaction.channel.purge(limit=amount)

    await interaction.followup.send(
        f"🧹 Deleted `{len(deleted)}` message(s).",
        ephemeral=True,
    )

    await log_action(
        interaction.guild,
        f"🧹 {interaction.user.mention} deleted {len(deleted)} message(s) in {interaction.channel.mention}.",
    )


@bot.tree.command(name="slowmode", description="Set channel slowmode.")
@app_commands.checks.has_permissions(manage_channels=True)
async def slowmode(
    interaction: discord.Interaction,
    seconds: app_commands.Range[int, 0, 21600],
):
    await interaction.channel.edit(
        slowmode_delay=seconds,
        reason=f"Slowmode changed by {interaction.user}",
    )

    await interaction.response.send_message(
        f"🐌 Slowmode set to `{seconds}` second(s)."
    )


@bot.tree.command(name="lock", description="Lock this channel.")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = False

    await interaction.channel.set_permissions(
        interaction.guild.default_role,
        overwrite=overwrite,
        reason=f"Channel locked by {interaction.user}",
    )

    await interaction.response.send_message("🔒 Channel locked.")


@bot.tree.command(name="unlock", description="Unlock this channel.")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = None

    await interaction.channel.set_permissions(
        interaction.guild.default_role,
        overwrite=overwrite,
        reason=f"Channel unlocked by {interaction.user}",
    )

    await interaction.response.send_message("🔓 Channel unlocked.")


# ============================================================
# HELP
# ============================================================

@bot.tree.command(name="help", description="Show Snowy's commands!")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🐾 Snowy's Commands",
        description="Cute, fun and useful commands!",
        color=discord.Color.orange(),
    )

    embed.add_field(
        name="🐾 Interactions",
        value=(
            "`/hug @user`  `/kiss @user`\n"
            "`/cuddle @user`  `/pat @user`\n"
            "`/boop @user`  `/highfive @user`\n"
            "`/wave @user`"
        ),
        inline=False,
    )

    embed.add_field(
        name="🛡️ Moderation",
        value=(
            "`/warn @user reason`\n"
            "`/warnings @user`\n"
            "`/clearwarnings @user`\n"
            "`/mute @user minutes reason`\n"
            "`/unmute @user`\n"
            "`/kick @user reason`\n"
            "`/ban @user reason`\n"
            "`/unban user_id`\n"
            "`/clear amount`\n"
            "`/slowmode seconds`\n"
            "`/lock`  `/unlock`"
        ),
        inline=False,
    )

    embed.add_field(
        name="⚙️ Configuration",
        value=(
            "`/config view`\n"
            "`/config welcome_channel`\n"
            "`/config welcome_toggle`\n"
            "`/config welcome_message`\n"
            "`/config welcome_title`\n"
            "`/config welcome_question`\n"
            "`/config log_channel`\n"
            "`/config autorole`\n"
            "`/config autorole_off`\n"
            "`/config reactionrole`\n"
            "`/config reactionrole_remove`"
        ),
        inline=False,
    )

    embed.add_field(
        name="🔧 Utility",
        value=(
            "`/serverinfo`  `/userinfo`\n"
            "`/avatar`  `/ping`\n"
            "`/coinflip`  `/dice`\n"
            "`/say`"
        ),
        inline=False,
    )

    embed.set_footer(text="Snowy • Furry Hangout 🐾")

    await interaction.response.send_message(embed=embed)


# ============================================================
# ERROR HANDLING
# ============================================================

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError,
):
    if isinstance(error, app_commands.errors.MissingPermissions):
        message = "❌ You don't have the required Discord permissions."
    elif isinstance(error, app_commands.errors.CheckFailure):
        message = str(error) or "❌ You don't have permission to use this command."
    else:
        print(f"Command error: {error}")
        message = "❌ Something went wrong while executing the command."

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


# ============================================================
# START
# ============================================================

bot.run(DISCORD_TOKEN)
