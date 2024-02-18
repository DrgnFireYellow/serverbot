import discord.ext.commands as discord_commands
import discord
from discord import app_commands
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

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

if os.path.exists("data.json"):
    with open("data.json") as datafile:
        data = json.load(datafile)
else:
    data = {"users": {}, "ids": []}


@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")

@tree.command(name="register")
async def register(ctx):
    if ctx.author in data["users"].keys():
        await ctx.response.send_message("You are already registered.")
    else:
        try:
            data['users'][ctx.author] = max(data['ids']) + 1
            data['ids'].append(max(data['ids']) + 1)
        except ValueError:
            data['users'][ctx.author] = 0
            data['ids'].append(0)
        await ctx.response.send_message(f"Registered with id of {data['users'][ctx.author]}")

@tree.command(name="create", description="Create a new Minecraft server")
async def create(ctx, server_name: str, server_version: str):
    dockerclient.containers.run("itzg/minecraft-server", detach=True, environment=[f"VERSION={server_version}", "EULA=TRUE"], ports={25565: 25565}, name=f"serverbot_{server_name}")
    await ctx.response.send_message(f'Created server `{server_name}` with Minecraft version {server_version}.')

@tree.command(name="start", description="Start an existing Minecraft server")
async def start(ctx, server_name: str):
    dockerclient.containers.get(f"serverbot_{server_name}").start()
    await ctx.response.send_message(f'Starting server `{server_name}`')
    
@tree.command(name="run", description="Run a command on a running Minecraft server")
async def run(ctx, server_name: str, command: str):
    dockerclient.containers.get(f"serverbot_{server_name}").exec_run(f"rcon-cli {command}")
    await ctx.response.send_message(f"Ran command `{command}` on server `{server_name}`")


@tree.command(name="log", description="Show the most recent log output from a Minecraft server")
async def log(ctx, server_name: str):
    await ctx.response.send_message(f"Most recent log output for server `{server_name}`: ```{dockerclient.containers.get(f'serverbot_{server_name}').logs()[-1000:].decode().replace("\\n", "\n")}```")

@tree.command(name="stop", description="Stop a running Minecraft server")
async def stop(ctx, server_name: str):
    dockerclient.containers.get(f"serverbot_{server_name}").stop()
    await ctx.response.send_message(f"Stopped server `{server_name}`")

client.run(args.bot_token)