# -*- coding: utf-8 -*-

import json
import logging

from PyQt6.QtWidgets import QMessageBox, QFileDialog
from sphere_base.utils.utils import dump_exception

logger = logging.getLogger(__name__)

# define file handler and set formatter
file_handler = logging.FileHandler(r'.\logs\\file_handler.log', 'w+')
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(funcName)s() : %(message)s')
file_handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)


class FileHandler:
    def __init__(self):
        super().__init__()

    @staticmethod
    def save_to_file(data_to_save, file_name_path, indent: int = 4):
        logger.info("Saving to file")

        try:
            file_to_save = json.dumps(data_to_save, indent=indent)
            with open(file_name_path, "w") as file:
                file.write(file_to_save)

        except FileNotFoundError:
            pass

        except Exception as e:
            dump_exception(e)
            logger.exception(f"Error File {file_name_path} cannot be saved: %s" % e)
            QMessageBox.critical(QMessageBox(), "Error", f"File {file_name_path} cannot be saved!")

    @staticmethod
    def load_from_file(file_name):
        """
        Load json from file

        :param file_name: path and name of the file to load from
        :type file_name: str

        """

        logger.info(f'loading json file {file_name}')

        try:
            with open(file_name, "r") as file:
                raw_data = file.read()
                data = json.loads(raw_data)
                # self.workspace.tab_widget.deserialize(data)
                return data

        except FileNotFoundError:
            logger.exception(f'file not found {file_name}')
            # QMessageBox.critical(QMessageBox(), "Error", f"File {file_name} does not exists!")

        except ValueError as e:
            logger.exception(f"Error File {file_name} invalid json file: %s" % e)
            QMessageBox.critical(QMessageBox(), "Error", f"File {file_name} invalid json file")

    def on_file_open(self):
        file_name = None

        dialog = QFileDialog()
        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter(self.get_file_dialog_filter())
        dialog.setDirectory(self.get_file_dialog_directory())

        if dialog.exec():
            file_name, _filter = dialog.getOpenFileName()

        try:
            if file_name:
                # return the data
                return self.load_from_file(file_name)

        except FileNotFoundError:
            logger.exception(f'file not found {file_name}')
            # QMessageBox.critical(QMessageBox(), "Error", f"File {file_name} does not exists!")

        except ValueError as e:
            logger.exception(f"Error File {file_name} invalid json file: %s" % e)
            QMessageBox.critical(QMessageBox(), "Error", f"File {file_name} invalid json file")

    @staticmethod
    def get_file_dialog_directory():
        """Returns starting directory for ``QFileDialog`` file open/save"""
        return ''

    @staticmethod
    def get_file_dialog_filter():
        """Returns ``str`` standard file open/save filter for ``QFileDialog``"""
        return 'MindMap (*.json);;All files (*)'
