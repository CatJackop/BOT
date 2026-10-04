import os,httpx
from fastapi import FastAPI,Request,Form
from fastapi.responses import HTMLResponse,RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import select
from database.db import get_session
from database.models import GuildSettings
app=FastAPI(title="CAT JACK Dashboard")
app.add_middleware(SessionMiddleware,secret_key=os.getenv("SESSION_SECRET","CHANGE-ME"),same_site="lax")
API="https://discord.com/api"
@app.get("/health")
async def health(): return {"status":"ok","service":"CAT JACK"}
def page(body):
 return HTMLResponse(f'''<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><style>
body{{margin:0;background:#0d1117;color:#f2f4f8;font-family:system-ui;padding:25px}}nav{{display:flex;justify-content:space-between;max-width:1000px;margin:auto;padding:10px 0 35px}}section,h1,.grid,.panel{{max-width:1000px;margin:auto}}section{{text-align:center;padding:70px 10px}}h1{{font-size:40px}}p{{color:#aeb7c4}}a{{color:#f4c84a;text-decoration:none}}.btn{{display:inline-block;background:#f4c84a;color:#17120a;border-radius:10px;padding:12px 18px;font-weight:800;margin-top:15px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:15px}}.card,.panel{{background:#161b22;border:1px solid #30363d;border-radius:14px;padding:20px}}.card small{{display:block;color:#8b949e;margin-top:8px}}label{{display:block;margin:18px 0}}input:not([type=checkbox]){{width:100%;padding:10px;margin-top:8px;background:#0d1117;color:white;border:1px solid #30363d;border-radius:8px}}.logo{{font-size:64px}}</style>{body}''')
@app.get("/",response_class=HTMLResponse)
async def home(request:Request):
 u=request.session.get("user")
 return page(f'<nav><b>🐱 CAT JACK</b><a href="/logout">Logout</a></nav><section><div class="logo">🐱</div><h1>CAT JACK</h1><p>Discord bot control dashboard</p><a class="btn" href="/servers">{"Manage Servers" if u else "Login with Discord"}</a></section>') if u else page('<section><div class="logo">🐱</div><h1>CAT JACK</h1><p>Discord bot control dashboard</p><a class="btn" href="/auth/login">Login with Discord</a></section>')
@app.get("/auth/login")
async def login():
 cid=os.getenv("DISCORD_CLIENT_ID"); red=os.getenv("DISCORD_REDIRECT_URI")
 if not cid or not red:return HTMLResponse("Configure Discord OAuth variables.",500)
 return RedirectResponse(f"{API}/oauth2/authorize?client_id={cid}&response_type=code&redirect_uri={red}&scope=identify%20guilds")
@app.get("/auth/callback")
async def callback(request:Request,code:str|None=None):
 if not code:return RedirectResponse("/")
 data={"client_id":os.getenv("DISCORD_CLIENT_ID"),"client_secret":os.getenv("DISCORD_CLIENT_SECRET"),"grant_type":"authorization_code","code":code,"redirect_uri":os.getenv("DISCORD_REDIRECT_URI")}
 async with httpx.AsyncClient(timeout=20) as c:
  r=await c.post(f"{API}/oauth2/token",data=data); r.raise_for_status(); t=r.json()["access_token"]; h={"Authorization":f"Bearer {t}"}
  user=(await c.get(f"{API}/users/@me",headers=h)).json(); guilds=(await c.get(f"{API}/users/@me/guilds",headers=h)).json()
 request.session["user"]=user; request.session["guilds"]=guilds; return RedirectResponse("/servers")
@app.get("/logout")
async def logout(request:Request): request.session.clear(); return RedirectResponse("/")
def manage(request,gid):
 for g in request.session.get("guilds",[]):
  if g["id"]==gid:
   p=int(g.get("permissions","0")); return bool(p&8 or p&32)
 return False
@app.get("/servers",response_class=HTMLResponse)
async def servers(request:Request):
 if "user" not in request.session:return RedirectResponse("/")
 cards=""
 for g in request.session.get("guilds",[]):
  if manage(request,g["id"]): cards+=f'<a class="card" href="/server/{g["id"]}">🏠 <b>{g["name"]}</b><small>Manage server</small></a>'
  else: cards+=f'<div class="card">🏠 <b>{g["name"]}</b><small>View only</small></div>'
 return page(f'<nav><b>🐱 CAT JACK</b><a href="/logout">Logout</a></nav><h1>Your Discord Servers</h1><div class="grid">{cards}</div>')
@app.get("/server/{gid}",response_class=HTMLResponse)
async def server(request:Request,gid:str):
 if "user" not in request.session:return RedirectResponse("/")
 if not manage(request,gid):return HTMLResponse("403 — Manage Server or Administrator permission required.",403)
 async with get_session() as db:
  r=await db.execute(select(GuildSettings).where(GuildSettings.guild_id==gid)); s=r.scalar_one_or_none()
  if not s:s=GuildSettings(guild_id=gid);db.add(s);await db.commit()
 ck=lambda x:"checked" if x else ""
 return page(f'<nav><b>🐱 CAT JACK</b><a href="/servers">← Servers</a></nav><h1>Server Settings</h1><form method="post" action="/server/{gid}/settings" class="panel"><label>Prefix<input name="prefix" value="{s.prefix}" maxlength="5"></label><label><input type="checkbox" name="welcome_enabled" {ck(s.welcome_enabled)}> Welcome</label><label><input type="checkbox" name="moderation_enabled" {ck(s.moderation_enabled)}> Moderation</label><label><input type="checkbox" name="tickets_enabled" {ck(s.tickets_enabled)}> Tickets</label><label><input type="checkbox" name="giveaways_enabled" {ck(s.giveaways_enabled)}> Giveaways</label><button class="btn">Save Settings</button></form>')
@app.post("/server/{gid}/settings")
async def save(request:Request,gid:str,prefix:str=Form("-"),welcome_enabled:str|None=Form(None),moderation_enabled:str|None=Form(None),tickets_enabled:str|None=Form(None),giveaways_enabled:str|None=Form(None)):
 if "user" not in request.session or not manage(request,gid):return HTMLResponse("Forbidden",403)
 async with get_session() as db:
  r=await db.execute(select(GuildSettings).where(GuildSettings.guild_id==gid));s=r.scalar_one_or_none()
  if not s:s=GuildSettings(guild_id=gid);db.add(s)
  s.prefix=prefix[:5] or "-";s.welcome_enabled=welcome_enabled=="on";s.moderation_enabled=moderation_enabled=="on";s.tickets_enabled=tickets_enabled=="on";s.giveaways_enabled=giveaways_enabled=="on";await db.commit()
 return RedirectResponse(f"/server/{gid}",303)
