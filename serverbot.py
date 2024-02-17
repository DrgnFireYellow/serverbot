import discord.ext.commands as discord_commands
import discord
import json
import os
import requests
import subprocess

intents = discord.Intents.default()
intents.message_content = True

bot = discord_commands.Bot("S.", intents=intents)

if os.path.exists("data.json"):
    with open("data.json") as datafile:
        data = json.load(datafile)
else:
    data = {"users": {}, "ids": []}


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command(name="register")
async def register(ctx):
    if ctx.author in data["users"].keys():
        await ctx.send("You are already registered.")
    else:
        try:
            data['users'][ctx.author] = max(data['ids']) + 1
            data['ids'].append(max(data['ids']) + 1)
        except ValueError:
            data['users'][ctx.author] = 0
            data['ids'].append(0)
        await ctx.send(f"Registered with id of {data['users'][ctx.author]}")

@bot.command(name="create")
async def create(ctx, server_name, server_version):
    os.mkdir(server_name)
    subprocess.run(["docker", "run", "-d", "-e", f"VERSION={server_version}", "-e", "EULA=TRUE", "-p", "25565:25565", "-v", f"./{server_name}:/data", "--name", f"serverbot_{server_name}", "itzg/minecraft-server"])
    await ctx.send(f'Created server "{server_name}" with Minecraft version {server_version}.')

@bot.command(name="start")
async def start(ctx, server_name):
    subprocess.run(["docker", "start", f"serverbot_{server_name}"])
    await ctx.send(f'Starting server "{server_name}"')
    
@bot.command(name="run")
async def run(ctx, server_name, command):
    subprocess.run(["docker", "exec", f"serverbot_{server_name}", "rcon-cli", command])
    await ctx.send(f"Ran command `{command}` on server {server_name}")


with open("bottoken.txt") as bottokenfile:
    bot.run(bottokenfile.read())