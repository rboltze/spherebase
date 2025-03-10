# -*- encoding: utf-8 -*-
"""
Module with some helper functions
"""

import traceback
from pprint import PrettyPrinter

from PyQt6.QtCore import QFile, QIODevice
from PyQt6.QtWidgets import QApplication

pp = PrettyPrinter(indent=4).pprint


def dump_exception(e=None):
    """
    Prints out Exception message with traceback to the console

    :param e: Exception to print out
    :type e: Exception
    """
    # print("%s EXCEPTION:" % e.__class__.__name__, e)
    # traceback.print_tb(e.__traceback__)
    traceback.print_exc()


def load_style_sheet(filename: str):
    """
    Loads a qss stylesheet to current QApplication instance

    :param filename: Filename of qss stylesheet
    :type filename: str
    """
    # print('STYLE loading:', filename)
    file = QFile(filename)
    file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text)
    stylesheet = file.readAll()
    # QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8'))
    QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8'))


def load_style_sheets(*args):
    """
    Loads multiple qss stylesheets. Concatenating them together and applying the final
    stylesheet to the current QApplication instance

    :param args: variable number of filenames of qss stylesheets
    :type args: str, str,...
    """
    res = ''
    for arg in args:
        file = QFile(arg)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        res += "\n" + str(stylesheet, encoding='utf-8')
    # QApplication.instance().setStyleSheet(res)
    QApplication.instance().setStyleSheet(res)
