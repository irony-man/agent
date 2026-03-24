from pydantic import BaseModel, Field
from typing import List, Optional

class PlayerStat(BaseModel):
    player_name: str = Field(..., description="Full name of the cricketer")
    stat_value: str = Field(..., description="The value (e.g. '102 runs', '5/20')")
    format: str = Field(..., description="Test, ODI, T20I, or IPL")
    match_date: Optional[str] = Field(None, description="Date of the record")

class CricketReport(BaseModel):
    summary: str = Field(..., description="Analytical summary of the player/record")
    stats_table: List[PlayerStat] = Field(..., description="List of structured stats")
    source_url: str = Field(..., description="The URL of the source used")