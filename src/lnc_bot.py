''' Script to automate Prospector SharePoint form fill '''
import logging
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, urlparse
from types import MappingProxyType
from dotenv import dotenv_values
from selenium_wrapper import Wrapper, WaitSec
from multi_lang import LANG
from excel_handler import get_dataframe_from_excel

EMPRESA_SELECTION_INDICA = 2
POSSUI_RO_SELECTION_NAO = 2

DURATION = MappingProxyType({
	'MÊS':    1,
	'MESES':  1,
	'ANO':   12,
	'ANOS':  12,
})

CLASSIFY = MappingProxyType({
	'RESIDENCIAL': 1,
	'COMERCIAL':   2,
	'INDUSTRIAL':  3,
})

PHASING = MappingProxyType({
	'MONO': 1,
	'BI':   2,
	'TRI':  3,
})

LOCATION = MappingProxyType({
	'OLHAL':           1,
	'FACHADA':         1,
	'PONTALETE':       1,
	'POSTE':           2,
	'POSTE EXISTENTE': 2,
	'POSTE 5':         3,
	'POSTE 7':         3,
	'PC':              4,
	'ARMÁRIO':         4,
})

if '__main__' == __name__:
	today_str = datetime.now().strftime('%Y%m%d')
	log_file = Path.cwd() / 'logs' / f'lnc_bot_{today_str}.log'
	logging.basicConfig(
		filename=log_file,
		level=logging.INFO)
	logger = logging.getLogger(__name__)

	configs = dotenv_values(Path.cwd() / 'lnc_bot.ini')
	data_path = configs.get('EVIDENCIAS')
	sheet_file = configs.get('PLANILHA')
	website = configs.get('WEBSITE')
	username = configs.get('USUARIO')
	password = configs.get('PALAVRA')

	if (
		not website or
		not username or
		not password or
		not sheet_file or
		not data_path or
		not Path(data_path).exists()
		):
		raise ValueError(LANG.MISSING_CONFIG)
	password = quote(password, safe="")
	parsed = urlparse(website)
	website = f'{parsed.scheme}://{username}:{password}@{parsed.hostname}{parsed.path}'

	worksheet = get_dataframe_from_excel(sheet_file)

	with Wrapper(website) as wrapper:
		for folder in Path(data_path).iterdir():
			if not folder.is_dir():
				continue
			if 'OK' in folder.name:
				logger.info(LANG.FOLDER_ALREADY_SENT, folder)
				continue

			facade_pictures = list(folder.glob('*.jpg'))
			inspection_videos = list(folder.glob('*.mp4'))
			document_picture = list(folder.glob('RG.pdf'))
			report_picture = list(folder.glob('REGULARIZAÇÃO.pdf'))
			donate_picture = list(folder.glob('DOAÇÃO.pdf'))

			if (
				not facade_pictures or
				not inspection_videos or
				document_picture is None or
				report_picture is None or
				donate_picture is None
				):
				raise ValueError(LANG.MISSING_FILES)

			facade_pictures = [str(x) for x in facade_pictures]
			inspection_videos = [str(x) for x in inspection_videos]
			document_picture = [str(x) for x in document_picture]
			report_picture = [str(x) for x in report_picture]
			donate_picture = [str(x) for x in donate_picture]

			rows = worksheet[worksheet['NOME'] == folder.name]
			if rows.empty:
				raise ValueError(LANG.CLIENT_DATA_NOT_FOUND.format(folder=folder.name))
			infos = rows.iloc[-1].to_dict()

			(value, text) = str(infos['TEMPO DE OCUPAÇÃO']).split(' ', 2)
			multiplier = DURATION.get(text)
			if not multiplier:
				raise ValueError()
			occupation_months = int(value) * multiplier

			wrapper.get_element('NOVO_REGISTRO_BTN', WaitSec.MED).click()
			wrapper.get_element('MODAL_PROSPECCAO_DIV', WaitSec.MED).click()
			wrapper.select_option('MODAL_GERENCIA_SEL', WaitSec.SHORT,
					'Gerência de Projetos Especiais e Grandes Clientes', True)
			wrapper.select_option('MODAL_COORDENA_SEL', WaitSec.SHORT,
					'Rec Projetos Especiais Ren', True)
			wrapper.get_element('MODAL_PROSPECTOR_TXT', WaitSec.NOW, infos['PROSPECTOR'])
			wrapper.select_radio('MODAL_EMPRESA_RDA', WaitSec.NOW, EMPRESA_SELECTION_INDICA)
			wrapper.select_radio('MODAL_POSSUI_RO_RDA', WaitSec.NOW, POSSUI_RO_SELECTION_NAO)
			wrapper.get_element('MODAL_CLIENTE_NOME_TXT', WaitSec.NOW, infos['NOME'])
			#wrapper.get_element('MODAL_CLIENTE_PN_TXT', WaitSec.NOW, infos['PN'])
			wrapper.get_element('MODAL_CLIENTE_CPF_TXT', WaitSec.NOW, infos['CPF/CNPJ'])
			wrapper.get_element('MODAL_ENDERECO_TXT', WaitSec.NOW, infos['ENDEREÇO'])
			wrapper.get_element('MODAL_COMPLEMENTO_TXT', WaitSec.NOW, infos['COMPLEMENTO'] or ' ')
			wrapper.get_element('MODAL_SUB-BAIRRO_TXT', WaitSec.NOW, infos['BAIRRO'])
			wrapper.get_element('MODAL_REFERENCIA_TXT', WaitSec.NOW, infos['MEDIDOR DE REFERÊNCIA'])
			wrapper.get_element('MODAL_ZONA-TRAFO_TXT', WaitSec.NOW, infos['ZONA/TRAFO'])
			wrapper.get_element('MODAL_TEMPO_MESES_TXT', WaitSec.NOW, str(occupation_months))
			wrapper.select_radio('MODAL_INSTALACAO_CLASSE_RDA', WaitSec.NOW,
					CLASSIFY[infos['CLASSE DA INSTALAÇÃO']])
			wrapper.select_radio('MODAL_INSTALACAO_FASES_RDA', WaitSec.NOW,
					PHASING[infos['TIPO DA INSTALAÇÃO']])
			wrapper.select_radio('MODAL_INSTALACAO_LOCAL_RDA', WaitSec.NOW,
					LOCATION[infos['LOCAL DA INSTALAÇÃO']])
			wrapper.get_element('MODAL_FACHADA_FOTO_FILE', WaitSec.NOW, facade_pictures)
			wrapper.get_element('MODAL_IRREGULAR_FOTO_FILE', WaitSec.NOW, inspection_videos)
			wrapper.get_element('MODAL_DOCUMENTO_FOTO_FILE', WaitSec.NOW, document_picture)
			wrapper.get_element('MODAL_DOCUMENTO_TERMO_FILE', WaitSec.NOW, report_picture)
			wrapper.get_element('MODAL_DOACAO_TERMO_FILE', WaitSec.NOW, donate_picture)
			form_element = wrapper.get_element('MODAL_PROSPECTOR_FORM', WaitSec.NOW)
			if not wrapper.driver.execute_script('return arguments[0].checkValidity();', form_element):
				raise ValueError(LANG.FORM_IS_NOT_VALID)
			wrapper.get_element('MODAL_SALVAR_BTN', WaitSec.NOW).click()
			new_folder_name = folder.parent / (folder.name + ' - OK')
			folder.rename(new_folder_name)
			logger.info(LANG.PROSPECTING_SENT, folder.name)
	input(LANG.FINISHING_PROGRAM_PROMPT)
