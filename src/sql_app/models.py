from sqlalchemy import Column, Integer, String, Float

from .database import Base


class BaseTransfer(Base):
    __abstract__ = True
    index = Column(Integer, primary_key=True, index=True)
    player_in = Column(String, unique=True)
    player_out = Column(String, index=True)
    chance_of_playing_this_round = Column(Integer)
    cost = Column(Float)
    team = Column(Integer)
    rank = Column(Integer, unique=True)
    score_delta = Column(Float)
    fpl_weekly_score = Column(Float)
    gameweek = Column(Integer)


class SuggestedGoalkeeperTransfers(BaseTransfer):
    __tablename__ = "suggested-goalkeeper-transfers"
    
class SuggestedDefenderTransfers(BaseTransfer):
    __tablename__ = "suggested-defender-transfers"  

class SuggestedMidfielderTransfers(BaseTransfer):
    __tablename__ = "suggested-midfielder-transfers"    
    
class SuggestedAttackerTransfers(BaseTransfer):
    __tablename__ = "suggested-attacker-transfers"
    
class SuggestedCombinedTransfers(BaseTransfer):
    __tablename__ = "suggested-combined-transfers"
