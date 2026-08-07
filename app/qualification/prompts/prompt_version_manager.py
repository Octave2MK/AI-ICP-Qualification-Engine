from app.qualification.prompts.versions import (
    PROMPT_VERSIONS,
)


class PromptVersionManager:

    DEFAULT_VERSION = "v2"

    @classmethod
    def get(
        cls,
        version: str | None = None,
    ):

        version = (
            version
            or cls.DEFAULT_VERSION
        )

        if version not in PROMPT_VERSIONS:
            raise ValueError(
                f"Unknown prompt version: {version}"
            )

        return PROMPT_VERSIONS[version]