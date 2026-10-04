import os,asyncio,threading
import discord
from discord.ext import commands
import uvicorn
from database.db import init_db
from dashboard.app import app
token=os.getenv("DISCORD_TOKEN")
intents=discord.Intents.default(); intents.guilds=True; intents.members=True; intents.message_content=True
bot=commands.Bot(command_prefix=os.getenv("BOT_PREFIX","-"),intents=intents,help_command=None)
@bot.event
async def on_ready(): print(f"CAT JACK online as {bot.user} | guilds={len(bot.guilds)}")
@bot.command()
async def ping(ctx): await ctx.send(f"🏓 CAT JACK • {round(bot.latency*1000)}ms")
@bot.command()
async def help(ctx):
 e=discord.Embed(title="🐱 CAT JACK",description="Use the dashboard to control your server.",color=discord.Color.gold())
 e.add_field(name="Commands",value="`-ping` — latency\n`-help` — help",inline=False); await ctx.send(embed=e)
def web(): uvicorn.run(app,host="0.0.0.0",port=int(os.getenv("PORT","8000")))
async def run():
 if not token: raise RuntimeError("DISCORD_TOKEN is missing in Railway Variables.")
 await init_db(); await bot.start(token)
if __name__=="__main__":
 threading.Thread(target=web,daemon=True).start(); asyncio.run(run())
