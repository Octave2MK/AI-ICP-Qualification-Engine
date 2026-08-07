import json
from pathlib import Path
from app.qualification.icp.icp_definition import ICPDefinition


class ICPLoader:
    def __init__(self, config_directory: str = "configs"):
        self._config_directory = Path(config_directory)

    def load(self, name: str) -> ICPDefinition:
        path = self._config_directory / f"{name}.json"

        if not path.exists():
            raise FileNotFoundError(
                f"ICP configuration not found: {path}"
            )
        
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)
        return ICPDefinition(**data)