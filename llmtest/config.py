from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class MySQLConfig(BaseModel):
    host: str = os.getenv("MYSQL_HOST", "localhost")
    port: int = int(os.getenv("MYSQL_PORT", "3306"))
    user: str = os.getenv("MYSQL_USER", "root")
    password: str = os.getenv("MYSQL_PASSWORD", "")
    database: str = os.getenv("MYSQL_DATABASE", "")
    databases: list[str] = []
    
    def __init__(self, **data):
        super().__init__(**data)
        # Parse multiple databases from MYSQL_DATABASE (comma-separated)
        db_string = os.getenv("MYSQL_DATABASE", "")
        if db_string:
            self.databases = [db.strip() for db in db_string.split(",") if db.strip()]
        if not self.databases and self.database:
            self.databases = [self.database]

class LLMConfig(BaseModel):
    use_llm: bool = os.getenv("USE_LLM", "true").lower() == "true"
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

MYSQL = MySQLConfig()
LLM = LLMConfig()
