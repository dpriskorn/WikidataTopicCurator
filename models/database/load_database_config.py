# import logging
#
# import yaml
# from pydantic import BaseModel
#
# from models.database.database_settings import DatabaseSettings
#
# logger = logging.getLogger(__name__)
#
#
# class LoadDatabaseConfig(BaseModel):
#     config_file_path: str = "config.yml"
#     config: DatabaseSettings | None = None
#
#     def load_config(self):
#         with open("config/database.yml") as yaml_file:
#             config_data = yaml.safe_load(yaml_file)
#             logger.debug("loaded database config")
#             # pprint(config_data)
#             db_settings = DatabaseSettings(**config_data["database"])
#             self.config = db_settings
#
#     @property
#     def get_db_uri(self) -> str:
#         if self.config is None:
#             raise ValueError("self.config was None")
#         return f"mysql://{self.config.username}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}"
