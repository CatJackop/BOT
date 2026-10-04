from sqlalchemy import String,Boolean
from sqlalchemy.orm import Mapped,mapped_column
from .db import Base
class GuildSettings(Base):
 __tablename__="guild_settings"
 guild_id:Mapped[str]=mapped_column(String(32),primary_key=True)
 prefix:Mapped[str]=mapped_column(String(5),default="-")
 welcome_enabled:Mapped[bool]=mapped_column(Boolean,default=False)
 moderation_enabled:Mapped[bool]=mapped_column(Boolean,default=True)
 tickets_enabled:Mapped[bool]=mapped_column(Boolean,default=False)
 giveaways_enabled:Mapped[bool]=mapped_column(Boolean,default=True)
