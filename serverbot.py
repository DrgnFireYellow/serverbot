import discord.ext.commands as discord_commands
import discord
import docker
import json
import os
import argparse


argumentparser = argparse.ArgumentParser()
argumentparser.add_argument("bot_token")
args = argumentparser.parse_args()


dockerclient = docker.from_env()
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
    dockerclient.containers.run("itzg/minecraft-server", detach=True, environment=[f"VERSION={server_version}", "EULA=TRUE"], ports={25565: 25565}, name=f"serverbot_{server_name}")
    await ctx.send(f'Created server `{server_name}` with Minecraft version {server_version}.')

@bot.command(name="start")
async def start(ctx, server_name):
    dockerclient.containers.get(f"serverbot_{server_name}").start()
    await ctx.send(f'Starting server `{server_name}`')
    
@bot.command(name="run")
async def run(ctx, server_name, command):
    dockerclient.containers.get(f"serverbot_{server_name}").exec_run(f"rcon-cli {command}")
    await ctx.send(f"Ran command `{command}` on server `{server_name}`")


@bot.command(name="log")
async def log(ctx, server_name):
    await ctx.send(f"Most recent log output for server `{server_name}`: ```{dockerclient.containers.get(f'serverbot_{server_name}').logs()[-1000:].decode().replace("\\n", "\n")}```")

@bot.command(name="stop")
async def stop(ctx, server_name):
    dockerclient.containers.get(f"serverbot_{server_name}").stop()
    await ctx.send(f"Stopped server `{server_name}`")

bot.run(args.bot_token)