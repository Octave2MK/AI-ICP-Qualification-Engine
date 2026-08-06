#%%
from dataclasses import dataclass


@dataclass(slots=True)
class ICPDecision:

    status: str

    reason: str

    priority: str