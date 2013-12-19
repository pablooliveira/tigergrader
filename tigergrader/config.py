from flask import Config

cfg = Config('.')
cfg.from_envvar('TIGERGRADER_SETTINGS')
