''' Module to retrieve message strings '''
# pylint: disable=too-few-public-methods
from pathlib import Path
from locale import getlocale
from dotenv import dotenv_values

class _I18n:
	''' class to retrieve message strings '''
	data: dict
	def __init__(self, lang: str) -> None:
		lang_file = Path.cwd() / 'Resources' / f'{lang}.lang'
		if not lang_file.is_file():
			raise FileNotFoundError(
				'Language resource file not found! '
				+ 'Check if language is available.')
		self.data = dotenv_values(str(lang_file))
	def __getattr__(self, name: str) -> str:
		value = self.data.get(name, '')
		if not value:
			raise KeyError(f'The language resource key {name} was not found!')
		return value

culture = getlocale()[0] or 'pt_BR'
LANG = _I18n(culture)
