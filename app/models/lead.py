from pydantic import BaseModel, Field
from typing import List, Optional
from app.constants import HOT_STATUS, COLD_STATUS

class Lead(BaseModel):
    business_name: str = Field(..., description="Name of the business")
    website_url: Optional[str] = Field(default="", description="Website URL")
    phone: Optional[str] = Field(default="", description="Phone number")
    email: Optional[str] = Field(default="", description="Email address")
    address: Optional[str] = Field(default="", description="Physical address")
    issues_found: List[str] = Field(default_factory=list, description="List of technical issues found")
    lead_status: str = Field(default=COLD_STATUS, description="HOT or COLD")

    def to_row(self) -> List[str]:
        return [
            self.business_name,
            self.website_url or "",
            self.phone or "",
            self.email or "",
            self.address or "",
            ", ".join(self.issues_found) if self.issues_found else "None",
            self.lead_status
        ]