# -*- coding: utf-8 -*-

"""
A module containing the Main Window menu class
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from sphere_base.sphere_universe_base.suv_utils import dump_exception
from widget_settings import Settings


class SphereMenu(QMenu):
    def __init__(self, main_win):
        super().__init__()

        self.main_win = main_win
        self._init_variables()
        self._init_menus()

    def _init_variables(self):
        self._active_split_window = None

    def _init_menus(self):
        self._create_actions()
        self._create_menus()
        self._create_status_bar()
        self._update_edit_menu()

    def _create_menus(self):
        """Create Menus for `File` and `Edit`"""
        self._create_file_menu()
        self._create_edit_menu()


        # self.windowMenu = self.main_win.menuBar().addMenu("&Window")
        # self.update_window_menu()
        # self.windowMenu.aboutToShow.connect(self.update_window_menu)

        self.main_win.menuBar().addSeparator()

        self.helpMenu = self.main_win.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.action_about)
        self.helpMenu.addAction(self.action_settings)

        self.edit_menu.aboutToShow.connect(self._update_edit_menu)

    def _create_actions(self):
        """Create basic `File` and `Edit` actions"""
        self.action_new = QAction('&New', self, shortcut='Ctrl+N', statusTip="Create new graph",
                                  triggered=self.on_file_new)
        self.action_open = QAction('&Open', self, shortcut='Ctrl+O', statusTip="Open file", triggered=self.on_file_open)
        self.action_save = QAction('&Save', self, shortcut='Ctrl+S', statusTip="Save file", triggered=self.on_file_save)
        self.action_save_as = QAction('Save &As...', self, shortcut='Ctrl+Shift+S', statusTip="Save file as...",
                                      triggered=self.on_file_save_as)
        self.action_exit = QAction('E&xit', self, shortcut='Ctrl+Q', statusTip="Exit application",
                                   triggered=self.main_win.close)
        self.action_undo = QAction('&Undo', self, shortcut='Ctrl+Z', statusTip="Undo last operation",
                                   triggered=self.on_edit_undo)
        self.action_redo = QAction('&Redo', self, shortcut='Ctrl+Shift+Z', statusTip="Redo last operation",
                                   triggered=self.on_edit_redo)
        self.action_cut = QAction('Cu&t', self, shortcut='Ctrl+X', statusTip="Cut to clipboard",
                                  triggered=self.on_edit_cut)
        self.action_copy = QAction('&Copy', self, shortcut='Ctrl+C', statusTip="Copy to clipboard",
                                   triggered=self.on_edit_copy)
        self.action_paste = QAction('&Paste', self, shortcut='Ctrl+V', statusTip="Paste from clipboard",
                                    triggered=self.on_edit_paste)
        self.action_delete = QAction('&Delete', self, shortcut='Del', statusTip="Delete _selected items",
                                     triggered=self.on_edit_delete)

        self.action_separator = QAction(self)
        self.action_separator.setSeparator(True)
        self.action_about = QAction("&About", self, statusTip="Show the application's About box",
                                    triggered=self.main_win.on_about)
        self.action_settings = QAction("&Settings", self, statusTip="Show the application's About box",
                                    triggered=self.open_settings_window)
        self._update_edit_menu()

    def open_settings_window(self):
        self.w = Settings(self.main_win)
        self.w.setGeometry(QRect(400, 400, 720, 575))
        self.w.setWindowFlags(self.windowFlags() | Qt.Dialog)
        self.w.show()

    def _create_file_menu(self):
        menu_bar = self.main_win.menuBar()
        self.file_menu = menu_bar.addMenu('&File')
        self.file_menu.addAction(self.action_new)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.action_open)
        self.file_menu.addAction(self.action_save)
        self.file_menu.addAction(self.action_save_as)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.action_exit)

    def _create_edit_menu(self):
        menu_bar = self.main_win.menuBar()
        self.edit_menu = menu_bar.addMenu('&Edit')
        self.edit_menu.addAction(self.action_undo)
        self.edit_menu.addAction(self.action_redo)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_cut)
        self.edit_menu.addAction(self.action_copy)
        self.edit_menu.addAction(self.action_paste)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_delete)

    def _create_settings_menu(self):
        menu_bar = self.main_win.menuBar()
        self.file_menu = menu_bar.addMenu('&Settings')

    def _create_status_bar(self):
        """Create Status bar """
        self.main_win.statusBar().showMessage("")
        self.status_mouse_pos = QLabel("")
        self.main_win.statusBar().addPermanentWidget(self.status_mouse_pos)
        self.main_win.statusBar().showMessage("Ready")

    def _update_edit_menu(self):
        if not self.get_win():
            self.action_paste.setEnabled(False)
            self.action_cut.setEnabled(False)
            self.action_copy.setEnabled(False)
            self.action_delete.setEnabled(False)
            self.action_undo.setEnabled(False)
            self.action_redo.setEnabled(False)
        elif self.get_win() == "detail":
            active = self.main_win.right_detail.editors_stack.currentWidget()
            hasMdiChild = (active is not None)

            self.action_paste.setEnabled(hasMdiChild)
            self.action_cut.setEnabled(hasMdiChild and active.hasSelectedItems())
            self.action_copy.setEnabled(hasMdiChild and active.hasSelectedItems())
            self.action_delete.setEnabled(hasMdiChild and active.hasSelectedItems())
            self.action_undo.setEnabled(hasMdiChild and active.canUndo())
            self.action_redo.setEnabled(hasMdiChild and active.canRedo())
        elif self.get_win() == "sphere_iot":
            active_sphere = True if self.main_win.sphere_widget.selected_sphere else False
            active = True if len(self.main_win.sphere_widget.selected_sphere_items) > 0 else False
            self.action_paste.setEnabled(active_sphere)
            self.action_cut.setEnabled(active)
            self.action_copy.setEnabled(active)
            self.action_delete.setEnabled(active)
            self.action_undo.setEnabled(active_sphere)
            self.action_redo.setEnabled(active_sphere)

    def reset_modified(self):
        # resetting the modified flag
        self.main_win.sphere_widget.uv_widget.uv.reset_has_been_modified()
        self.main_win.sphere_widget.on_selection_changed(None, None)

    def get_win(self):
        # helper function to get the active split window
        pass
        #return self.main_win.split.get_active_split_window()

    def get_sphere(self):
        # helper function to get the active target sphere_base from the sphere_iot
        return self.main_win.sphere_widget.uv_widget.uv.target_sphere

    def get_detail(self):
        # helper function to get to the stack with detail editors
        pass
        # return self.main_win.split.right_detail

    def on_edit_undo(self):
        if self.get_win() == "detail":
            self.get_detail().onEditUndo()
        elif self.get_win() == "sphere_iot":
            self.get_sphere().history.undo()

    def on_edit_redo(self):
        if self.get_win() == "detail":
            self.get_detail().onEditRedo()
        elif self.get_win() == "sphere_iot":
            self.get_sphere().history.redo()

    def on_edit_delete(self):
        if self.get_win() == "detail":
            self.get_detail().onEditDelete()
        elif self.get_win() == "sphere_iot":
            self.get_sphere().delete_selected_items()

    def on_edit_cut(self):
        if self.get_win() == "detail":
            self.get_detail().onEditCut()
        elif self.get_win() == "sphere_iot":
            self.get_sphere().edit_cut()

    def on_edit_copy(self):
        if self.get_win() == "detail":
            self.get_detail().onEditCopy()
        elif self.get_win() == "sphere_iot":
            self.get_sphere().edit_copy()

    def on_edit_paste(self):
        if self.get_win() == "detail":
            self.get_detail().onEditPaste()
        elif self.get_win() == "sphere_iot":
            self.get_sphere().edit_paste()

    def on_file_new(self):
        self.main_win.filename = ""
        self.main_win.sphere_widget.uv_widget.uv_new()
        self.reset_modified()
        self.main_win.set_title()

    def on_file_open(self):
        fnames, filter = QFileDialog.getOpenFileNames(self, 'Open graph from file', self.getFileDialogDirectory(),
                                                      self.getFileDialogFilter())
        try:
            for fname in fnames:
                if fname:
                    self.main_win.sphere_widget.uv_widget.load_from_file(fname)
                    self.main_win.filename = fname
                    self.reset_modified()
                    self.main_win.set_title()

        except Exception as e:
            dump_exception(e)

    def on_file_save(self):
        """Handle File Save operation"""

        if not self.main_win.filename:
            return self.on_file_save_as()

        self.file_save(self.main_win.filename)
        self.main_win.statusBar().showMessage("Successfully saved %s" % self.main_win.filename, 5000)
        return True

    def on_file_save_as(self):
        """Handle File Save As operation"""

        file_name, filter = QFileDialog.getSaveFileName(self, 'Save graph to file', self.getFileDialogDirectory(),
                                                        self.getFileDialogFilter())
        if file_name == '':
            return False

        self.file_save(file_name)
        self.main_win.statusBar().showMessage("Successfully saved as %s" % self.main_win.filename, 5000)
        return True

    def file_save(self, filename=None):
        if filename is not None:
            self.main_win.filename = filename

        self.main_win.sphere_widget.uv_widget.save_to_file(self.main_win.filename)
        QApplication.restoreOverrideCursor()

        self.reset_modified()
        self.main_win.set_title()
        return True

    def getFileDialogDirectory(self):
        """Returns starting directory for ``QFileDialog`` file open/save"""
        return ''

    def getFileDialogFilter(self):
        """Returns ``str`` standard file open/save filter for ``QFileDialog``"""
        return 'Graph (*.json);;All files (*)'

    def has_been_modified(self):
        return self.main_win.sphere_widget.uv_widget.uv.is_modified()



