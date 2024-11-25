from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=['settings.toml'],
    environments=True,
)

print(settings.DATABASE_URL)
print(settings.SECRET_KEY)
