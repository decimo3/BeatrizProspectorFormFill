''' Module to get dataframe from Excel file '''
import os
import logging
import pandas
import openpyxl
from multi_lang import LANG

class WorksheetNotFoundException(Exception):
	''' Exception to inform that worksheet was not found '''

def get_dataframe_from_excel(file_path: str) -> pandas.DataFrame:
	''' Function to get DataFrame from Excel file '''
	logger = logging.getLogger(__name__)
	if not os.path.exists(file_path):
		raise FileNotFoundError(LANG.EXCEL_FILE_NOT_FOUND)
	logger.info(LANG.EXCEL_LOADING_FILE, file_path)
	workbook = openpyxl.open(file_path)
	worksheet = workbook.active
	if not worksheet:
		raise WorksheetNotFoundException(LANG.EXCEL_WORKSHEET_ERROR)
	rows = worksheet.iter_rows(values_only=True)
	head = next(rows)
	body = list(rows)
	dataframe = pandas.DataFrame(body, columns=head)
	logger.debug(LANG.EXCEL_WORKSHEET_LOADED)
	return dataframe
