import discord
from discord.ext import commands
import requests
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------- ROBLOX FUNCTIONS ----------

def get_user(username_or_id):
    if username_or_id.isdigit():
        r = requests.get(f"https://users.roblox.com/v1/users/{username_or_id}")
        return r.json()

    r = requests.post(
        "https://users.roblox.com/v1/usernames/users",
        json={"usernames": [username_or_id]}
    )
    data = r.json()
    if not data["data"]:
        return None

    user_id = data["data"][0]["id"]
    return requests.get(f"https://users.roblox.com/v1/users/{user_id}").json()

def get_followers(user_id):
    r = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/followers/count")
    return r.json()["count"]

def get_group(group_id):
    return requests.get(f"https://groups.roblox.com/v1/groups/{group_id}").json()

def get_game(place_id):
    r = requests.get(
        f"https://games.roblox.com/v1/games/multiget-place-details?placeIds={place_id}"
    )
    return r.json()[0]

def get_game_stats(universe_id):
    votes = requests.get(
        f"https://games.roblox.com/v1/games/{universe_id}/votes"
    ).json()
    game = requests.get(
        f"https://games.roblox.com/v1/games?universeIds={universe_id}"
    ).json()["data"][0]

    return votes["upVotes"], game["visits"], game["favoritedCount"]

def get_asset_favorites(asset_id):
    r = requests.get(
        f"https://catalog.roblox.com/v1/favorites/assets/{asset_id}/count"
    )
    return r.json()["favoritesCount"]

def get_bundle_favorites(bundle_id):
    r = requests.get(
        f"https://catalog.roblox.com/v1/favorites/bundles/{bundle_id}/count"
    )
    return r.json()["favoritesCount"]

# ---------- COMMANDS ----------

@bot.command()
async def followers(ctx, user):
    u = get_user(user)
    if not u:
        await ctx.send("User not found.")
        return

    count = get_followers(u["id"])
    await ctx.send(
        f"**User:** {u['name']}\n"
        f"**ID:** {u['id']}\n"
        f"**Followers:** {count}"
    )

@bot.command()
async def group(ctx, group_id):
    g = get_group(group_id)
    await ctx.send(
        f"**Group:** {g['name']}\n"
        f"**ID:** {g['id']}\n"
        f"**Members:** {g['memberCount']}"
    )

@bot.command()
async def game(ctx, place_id):
    game = get_game(place_id)
    likes, visits, favs = get_game_stats(game["universeId"])

    await ctx.send(
        f"**Game:** {game['name']}\n"
        f"**Place ID:** {place_id}\n"
        f"**Universe ID:** {game['universeId']}\n"
        f"👍 Likes: {likes}\n"
        f"⭐ Favorites: {favs}\n"
        f"👁 Visits: {visits}"
    )

@bot.command()
async def asset(ctx, asset_id):
    favs = get_asset_favorites(asset_id)
    await ctx.send(
        f"**Asset ID:** {asset_id}\n"
        f"⭐ Favorites: {favs}"
    )

@bot.command()
async def bundle(ctx, bundle_id):
    favs = get_bundle_favorites(bundle_id)
    await ctx.send(
        f"**Bundle ID:** {bundle_id}\n"
        f"⭐ Favorites: {favs}"
    )

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

# ---------- START ----------

bot.run(os.getenv("DISCORD_TOKEN"))
