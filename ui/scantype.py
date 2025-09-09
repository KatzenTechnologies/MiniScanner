from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox, QLabel,
    QAbstractItemView, QTabWidget, QDialog, QGroupBox, QMenu, QLineEdit,
    QHeaderView, QInputDialog, QCheckBox, QTreeWidget, QTreeWidgetItem, QListWidget, QComboBox
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit,
    QCheckBox, QComboBox, QSpinBox, QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QAction
import os
import json


class PluginConfigTab(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.current_config = None
        self.current_localization = None
        self.current_hidden_vars = []
        self.value_widgets = {}
        self.schemes = {}
        main_layout = QHBoxLayout()
        self.tr = api.chosen_language.translate
        plugins_panel = QGroupBox(self.tr("plugins"))
        plugins_layout = QVBoxLayout()
        self.plugins_list = QListWidget()
        self.plugins_list.itemSelectionChanged.connect(self.plugin_selected)
        plugins_layout.addWidget(self.plugins_list)
        plugins_panel.setLayout(plugins_layout)
        config_panel = QGroupBox(self.tr("config_settings"))
        config_layout = QVBoxLayout()
        self.params_table = QTableWidget(0, 4)
        self.params_table.setHorizontalHeaderLabels([
            self.tr("param_name"), self.tr("param_type"), self.tr("param_value"), self.tr("description")
        ])
        self.params_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.params_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.params_table.setColumnWidth(0, 200)
        self.params_table.setColumnWidth(1, 100)
        self.params_table.setColumnWidth(2, 200)
        self.params_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.params_table.setWordWrap(True)
        config_layout.addWidget(self.params_table)
        self.save_btn = QPushButton(self.tr("save_button"))
        self.save_btn.clicked.connect(self.save_config)
        config_layout.addWidget(self.save_btn, 0, Qt.AlignRight)
        config_panel.setLayout(config_layout)
        main_layout.addWidget(plugins_panel, 1)
        main_layout.addWidget(config_panel, 3)
        self.setLayout(main_layout)
        self.load_plugins()

    def load_plugins(self):
        self.plugins_list.clear()
        if hasattr(self.api, '_pl_configs'):
            for name in self.api._pl_configs.keys():
                self.plugins_list.addItem(name)

    def plugin_selected(self):
        selected_items = self.plugins_list.selectedItems()
        if not selected_items:
            self.current_config = None
            self.current_localization = None
            self.current_hidden_vars = []
            self.schemes = {}
            self.params_table.setRowCount(0)
            return
        name = selected_items[0].text()
        if name in self.api._pl_configs:
            config_data = self.api._pl_configs[name]
            self.current_config = config_data[0]
            self.current_localization = config_data[1]
            self.current_hidden_vars = config_data[2]
            self.schemes = config_data[3]
        else:
            self.current_config = None
            self.current_localization = None
            self.current_hidden_vars = []
            self.schemes = {}
        self.update_params_table()

    def update_params_table(self):
        self.params_table.setRowCount(0)
        self.value_widgets.clear()
        if not self.current_config or self.current_config.data is None:
            return
        params = []
        for key, value in self.current_config.data.items():
            if key in self.current_hidden_vars:
                continue
            params.append((key, value))
        self.params_table.setRowCount(len(params))
        for i, (key, value) in enumerate(params):
            scheme = self.schemes.get(key, {})
            if self.current_localization:
                display_key = self.current_localization.translate(key)
                desc_key = f"{key}_desc"
                description = self.current_localization.translate(desc_key, default="")
            else:
                display_key = key
                description = ""
            item_key = QTableWidgetItem(display_key)
            item_key.setData(Qt.UserRole, key)
            self.params_table.setItem(i, 0, item_key)
            if isinstance(value, bool):
                type_name = self.tr("boolean_type")
            elif isinstance(value, int):
                type_name = self.tr("integer_type")
            elif isinstance(value, float):
                type_name = self.tr("float_type")
            elif isinstance(value, str):
                type_name = self.tr("string_type")
            else:
                type_name = self.tr("object_type")
            type_item = QTableWidgetItem(type_name)
            self.params_table.setItem(i, 1, type_item)
            desc_item = QTableWidgetItem(description)
            self.params_table.setItem(i, 3, desc_item)
            widget = None
            if isinstance(value, bool):
                chk = QCheckBox()
                chk.setChecked(value)
                chk.stateChanged.connect(lambda state, k=key: self.toggle_boolean(k, state))
                widget = chk
            elif isinstance(value, (int, float, str)) and scheme:
                if scheme.get("type") == "combobox":
                    cb = QComboBox()
                    for v in scheme.get("values", []):
                        cb.addItem(str(v))
                    if str(value) in [str(v) for v in scheme.get("values", [])]:
                        cb.setCurrentText(str(value))
                    cb.currentTextChanged.connect(lambda val, k=key: self.value_changed(k, val))
                    widget = cb
                elif isinstance(value, (int, float)) and "values" in scheme:
                    sb = QSpinBox()
                    vals = scheme["values"]
                    if vals:
                        sb.setMinimum(min(vals))
                        sb.setMaximum(max(vals))
                    sb.setValue(int(value))
                    sb.valueChanged.connect(lambda val, k=key: self.value_changed(k, val))
                    widget = sb
            if not widget:
                edit = QLineEdit(str(value))
                edit.setObjectName(f"edit_{key}")
                widget = edit
                self.value_widgets[key] = edit
            self.params_table.setCellWidget(i, 2, widget)
            self.value_widgets[key] = widget
        self.params_table.resizeRowsToContents()
        self.params_table.resizeColumnToContents(0)
        self.params_table.resizeColumnToContents(1)
        self.params_table.resizeColumnToContents(2)
        self.update_dependencies()

    def update_dependencies(self):
        for key, scheme in self.schemes.items():
            widget = self.value_widgets.get(key)
            if not widget:
                continue
            enabled = True
            if "enabled_if" in scheme:
                dep = scheme["enabled_if"]
                dep_val = self.get_value(dep)
                enabled = bool(dep_val)
            if "disabled_if" in scheme:
                dep = scheme["disabled_if"]
                dep_val = self.get_value(dep)
                if dep_val:
                    enabled = False
            widget.setEnabled(enabled)

    def get_value(self, key):
        if key not in self.value_widgets:
            return self.current_config.data.get(key)
        widget = self.value_widgets[key]
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, QLineEdit):
            return widget.text()
        elif isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QSpinBox):
            return widget.value()
        return self.current_config.data.get(key)

    def value_changed(self, key, value):
        if not self.current_config:
            return
        self.current_config.data[key] = value
        self.update_dependencies()

    def toggle_boolean(self, key, state):
        if not self.current_config or self.current_config.data is None:
            return
        self.current_config.data[key] = state == Qt.Checked
        self.current_config.save()
        self.update_dependencies()

    def save_config(self):
        if not self.current_config:
            return
        for key, widget in self.value_widgets.items():
            if key in self.current_config.data:
                if isinstance(widget, QLineEdit):
                    val = widget.text()
                    orig = self.current_config.data[key]
                    if isinstance(orig, int):
                        try:
                            self.current_config.data[key] = int(val)
                        except ValueError:
                            pass
                    elif isinstance(orig, float):
                        try:
                            self.current_config.data[key] = float(val)
                        except ValueError:
                            pass
                    else:
                        self.current_config.data[key] = val
                elif isinstance(widget, QCheckBox):
                    self.current_config.data[key] = widget.isChecked()
                elif isinstance(widget, QComboBox):
                    self.current_config.data[key] = widget.currentText()
                elif isinstance(widget, QSpinBox):
                    self.current_config.data[key] = widget.value()
        self.current_config.save()
        QMessageBox.information(self, "✅", self.api.chosen_language.translate("config_saved"))



class ScanTab(QWidget):
    def __init__(self, api, on_scan_callback, get_excludes):
        super().__init__()
        self.api = api
        self.on_scan_callback = on_scan_callback
        self.selected_paths = []
        self.setAcceptDrops(True)
        self.tr = api.chosen_language.translate
        self.exclusions_config = get_excludes()
        self.excluded_paths = self.exclusions_config.get("paths", [])
        layout = QVBoxLayout()
        self.scan_memory_checkbox = QCheckBox(self.tr("scan_memory"))
        self.scan_memory_checkbox.setChecked(True)
        layout.addWidget(self.scan_memory_checkbox)
        scan_btns_layout = QHBoxLayout()
        self.full_btn = QPushButton(self.tr("scan_full"))
        self.quick_btn = QPushButton(self.tr("scan_quick"))
        self.custom_btn = QPushButton(self.tr("scan_custom"))
        scan_btns_layout.addWidget(self.full_btn)
        scan_btns_layout.addWidget(self.quick_btn)
        scan_btns_layout.addWidget(self.custom_btn)
        selection_group = QGroupBox(self.tr("custom_group"))
        selection_layout = QVBoxLayout()
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels([self.tr("custom_table_header"), self.tr("type_column")])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.setWordWrap(True)
        add_btns_layout = QHBoxLayout()
        self.add_files_btn = QPushButton(self.tr("add_files"))
        self.add_folder_btn = QPushButton(self.tr("add_folders"))
        add_btns_layout.addWidget(self.add_files_btn)
        add_btns_layout.addWidget(self.add_folder_btn)
        self.clear_btn = QPushButton(self.tr("clear_custom"))
        selection_layout.addLayout(add_btns_layout)
        selection_layout.addWidget(self.clear_btn)
        selection_layout.addWidget(self.table)
        selection_group.setLayout(selection_layout)
        exclusions_group = QGroupBox(self.tr("exclusions_group"))
        exclusions_layout = QVBoxLayout()
        self.manage_exclusions_btn = QPushButton(self.tr("manage_exclusions"))
        exclusions_layout.addWidget(self.manage_exclusions_btn)
        exclusions_group.setLayout(exclusions_layout)
        self.full_btn.clicked.connect(lambda: self.on_scan_callback("full", []))
        self.quick_btn.clicked.connect(lambda: self.on_scan_callback("quick", []))
        self.custom_btn.clicked.connect(self.start_custom_scan)
        self.add_files_btn.clicked.connect(self.add_files)
        self.add_folder_btn.clicked.connect(self.add_folder)
        self.clear_btn.clicked.connect(self.clear_paths)
        self.manage_exclusions_btn.clicked.connect(self.manage_exclusions)
        layout.addLayout(scan_btns_layout)
        layout.addWidget(selection_group)
        layout.addWidget(exclusions_group)
        self.setLayout(layout)
        self.setMinimumSize(700, 500)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, self.tr("select_files"))
        if files:
            self.add_paths([(f, "file") for f in files])

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.tr("select_folder"))
        if folder:
            self.add_paths([(folder, "folder")])

    def add_paths(self, paths):
        new_paths = [p for p in paths if p[0] not in [item[0] for item in self.selected_paths] and p[0] not in self.excluded_paths]
        self.selected_paths.extend(new_paths)
        self.update_table()

    def update_table(self):
        self.table.setRowCount(len(self.selected_paths))
        for i, (path, path_type) in enumerate(self.selected_paths):
            path_item = QTableWidgetItem(path)
            self.table.setItem(i, 0, path_item)
            type_text = self.tr("file") if path_type == "file" else self.tr("folder")
            type_item = QTableWidgetItem(type_text)
            self.table.setItem(i, 1, type_item)
        self.table.resizeRowsToContents()
        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)

    def clear_paths(self):
        self.selected_paths.clear()
        self.update_table()

    def start_custom_scan(self):
        if not self.selected_paths:
            QMessageBox.warning(self, "❌", self.tr("custom_empty"))
            return
        filtered_paths = [p[0] for p in self.selected_paths if p[0] not in self.excluded_paths]
        self.on_scan_callback("custom", filtered_paths)

    def exclude_selected(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "⚠️", self.tr("no_selection"))
            return
        rows = set(item.row() for item in selected_items)
        paths_to_exclude = [self.selected_paths[row][0] for row in rows]
        for row in sorted(rows, reverse=True):
            del self.selected_paths[row]
        for path in paths_to_exclude:
            if path not in self.excluded_paths:
                self.excluded_paths.append(path)
        self.exclusions_config["paths"] = self.excluded_paths
        self.update_table()
        QMessageBox.information(self, "✅", self.tr("excluded_success"))

    def manage_exclusions(self):
        dialog = ExclusionsDialog(self.api, self.excluded_paths, self)
        if dialog.exec() == QDialog.Accepted:
            self.excluded_paths = dialog.get_exclusions()
            self.exclusions_config["paths"] = self.excluded_paths
            self.exclusions_config.save()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        exclude_action = QAction(self.tr("exclude_selected"), self)
        exclude_action.triggered.connect(self.exclude_selected)
        remove_action = QAction(self.tr("remove_from_list"), self)
        remove_action.triggered.connect(self.remove_selected)
        menu.addAction(exclude_action)
        menu.addAction(remove_action)
        menu.exec(self.table.mapToGlobal(pos))

    def remove_selected(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        rows = set(item.row() for item in selected_items)
        for row in sorted(rows, reverse=True):
            del self.selected_paths[row]
        self.update_table()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        paths = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                paths.append((path, "file"))
            elif os.path.isdir(path):
                paths.append((path, "folder"))
        valid_paths = [p for p in paths if p[0] not in self.excluded_paths]
        self.add_paths(valid_paths)

    def scan_memory_enabled(self):
        return self.scan_memory_checkbox.isChecked()


class ExclusionsDialog(QDialog):
    def __init__(self, api, exclusions, parent=None):
        super().__init__(parent)
        self.api = api
        self.excluded_paths = exclusions.copy()
        self.tr = api.chosen_language.translate
        self.setWindowTitle(self.tr("exclusions_title"))
        self.setMinimumSize(600, 400)
        self.setAcceptDrops(True)
        layout = QVBoxLayout()
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels([self.tr("excluded_table_header"), self.tr("type_column")])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.setWordWrap(True)
        self.populate_table()
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton(self.tr("add_exclusion"))
        self.remove_btn = QPushButton(self.tr("remove_exclusion"))
        self.add_btn.clicked.connect(self.show_add_menu)
        self.remove_btn.clicked.connect(self.remove_exclusion)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        dialog_btns = QHBoxLayout()
        self.ok_btn = QPushButton(self.tr("ok_button"))
        self.cancel_btn = QPushButton(self.tr("cancel_button"))
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        dialog_btns.addStretch()
        dialog_btns.addWidget(self.ok_btn)
        dialog_btns.addWidget(self.cancel_btn)
        layout.addWidget(self.table)
        layout.addLayout(btn_layout)
        layout.addLayout(dialog_btns)
        self.setLayout(layout)

    def populate_table(self):
        self.table.setRowCount(len(self.excluded_paths))
        for i, path in enumerate(self.excluded_paths):
            path_item = QTableWidgetItem(path)
            self.table.setItem(i, 0, path_item)
            path_type = self.tr("file") if os.path.isfile(path) else self.tr("folder")
            type_item = QTableWidgetItem(path_type)
            self.table.setItem(i, 1, type_item)
        self.table.resizeRowsToContents()
        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)

    def show_add_menu(self):
        menu = QMenu(self)
        add_file_action = QAction(self.tr("add_file_exclusion"), self)
        add_file_action.triggered.connect(lambda: self.add_exclusion("file"))
        add_folder_action = QAction(self.tr("add_folder_exclusion"), self)
        add_folder_action.triggered.connect(lambda: self.add_exclusion("folder"))
        menu.addAction(add_file_action)
        menu.addAction(add_folder_action)
        menu.exec(self.add_btn.mapToGlobal(self.add_btn.rect().bottomLeft()))

    def add_exclusion(self, item_type):
        if item_type == "file":
            files, _ = QFileDialog.getOpenFileNames(self, self.tr("select_files"))
            new_paths = [f for f in files if f not in self.excluded_paths]
        else:
            folder = QFileDialog.getExistingDirectory(self, self.tr("select_folder"))
            new_paths = [folder] if folder and folder not in self.excluded_paths else []
        self.excluded_paths.extend(new_paths)
        self.populate_table()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        remove_action = QAction(self.tr("remove_exclusion"), self)
        remove_action.triggered.connect(self.remove_exclusion)
        menu.addAction(remove_action)
        menu.exec(self.table.mapToGlobal(pos))

    def remove_exclusion(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        rows = set(item.row() for item in selected)
        for row in sorted(rows, reverse=True):
            del self.excluded_paths[row]
        self.populate_table()

    def get_exclusions(self):
        return self.excluded_paths

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        paths = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path) or os.path.isdir(path):
                paths.append(path)
        new_paths = [p for p in paths if p not in self.excluded_paths]
        self.excluded_paths.extend(new_paths)
        self.populate_table()


class QuarantineTab(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.quarantine = api.quarantine
        self.tr = api.chosen_language.translate
        layout = QVBoxLayout()
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([
            self.tr("q_id"), self.tr("q_file"), self.tr("q_threat"), self.tr("q_source")
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        self.table.setWordWrap(True)
        self.refresh_btn = QPushButton(self.tr("q_refresh"))
        self.refresh_btn.clicked.connect(self.populate_table)
        self.restore_btn = QPushButton(self.tr("q_restore"))
        self.restore_btn.clicked.connect(self.restore_selected)
        self.delete_btn = QPushButton(self.tr("q_delete"))
        self.delete_btn.clicked.connect(self.delete_selected)
        self.action_combo = QComboBox()
        self.action_combo.addItems([self.tr("q_delete"), self.tr("q_restore")])
        self.apply_all_btn = QPushButton(self.tr("apply_all"))
        self.apply_all_btn.clicked.connect(self.apply_all)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.restore_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.action_combo)
        btn_layout.addWidget(self.apply_all_btn)
        layout.addLayout(btn_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.setMinimumSize(700, 400)
        self.populate_table()

    def populate_table(self):
        records = self.quarantine.get_records()
        self.table.setSortingEnabled(False)
        self.table.clearContents()
        self.table.setRowCount(len(records))
        for i, r in enumerate(records):
            id_val = str(r.get("id", "N/A"))
            full_path = str(r.get("file", ""))
            threat_val = str(r.get("threat", "Unknown"))
            source_val = str(r.get("source", "N/A"))
            id_item = QTableWidgetItem(id_val)
            self.table.setItem(i, 0, id_item)
            file_item = QTableWidgetItem(full_path)
            file_item.setToolTip(full_path)
            file_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            file_item.setFlags(file_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            file_item.setText(full_path)
            self.table.setItem(i, 1, file_item)
            threat_item = QTableWidgetItem(threat_val)
            self.table.setItem(i, 2, threat_item)
            source_item = QTableWidgetItem(source_val)
            self.table.setItem(i, 3, source_item)
        self.table.setWordWrap(True)
        self.table.setColumnWidth(1, 300)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSortingEnabled(True)

    def get_selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        if not item:
            return None
        try:
            return int(item.text())
        except ValueError:
            return None

    def restore_selected(self):
        rid = self.get_selected_id()
        if rid is not None:
            self.quarantine.restore_id(rid)
            self.populate_table()
            QMessageBox.information(self, "✅", self.tr("q_restored", id=rid))
        else:
            QMessageBox.warning(self, "⚠️", self.tr("no_selection"))

    def delete_selected(self):
        rid = self.get_selected_id()
        if rid is not None:
            self.quarantine.remove_id(rid)
            self.populate_table()
            QMessageBox.information(self, "🗑️", self.tr("q_deleted", id=rid))
        else:
            QMessageBox.warning(self, "⚠️", self.tr("no_selection"))

    def apply_all(self):
        action = self.action_combo.currentText()
        records = self.quarantine.get_records()
        for r in records:
            rid = r.get("id")
            if rid is None:
                continue
            if action == self.tr("q_delete"):
                self.quarantine.remove_id(rid)
            elif action == self.tr("q_restore"):
                self.quarantine.restore_id(rid)
        self.populate_table()
        QMessageBox.information(self, "✅", self.tr("action_applied_all"))


class AboutTab(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.tr = api.chosen_language.translate
        layout = QVBoxLayout()
        html = f"""
        <h2>MiniScanner</h2>
        <p>{self.tr("about_description")}</p>
        <p><b>{self.tr("about_version")}:</b> {getattr(api, "full_version", "Unknown")}</p>
        <p><b>{self.tr("about_author")}:</b> KatzenTechnologies</p>
        <h3>{self.tr("about_thanks")}</h3>
        <ul>
            <li>horsicq</li>
            <li>h0rrif</li>
            <li>KdR</li>
        </ul>
        <h3>{self.tr("about_used_components")}</h3>
        <ul>
            <li>Darktrace, Virustotal</li>
        </ul>
        <h2>R.I.P. Motya (?? Aug 2010 - 5 Sep 2025). Ingebeplandi oloe maasehdee sine!</h2>
        """
        label = QLabel(html)
        label.setAlignment(Qt.AlignTop)
        label.setWordWrap(True)
        layout.addWidget(label)
        self.setLayout(layout)


class ScannerGUI(QDialog):
    def __init__(self, api, get_excludes):
        super().__init__()
        self.api = api
        self.scan_type = None
        self.scan_paths = []
        self.setWindowTitle("MiniScanner")
        self.setMinimumSize(800, 500)
        self.tabs = QTabWidget()
        self.scan_tab = ScanTab(api, self.handle_scan, get_excludes)
        self.quarantine_tab = QuarantineTab(api)
        self.config_tab = PluginConfigTab(api)
        self.about_tab = AboutTab(api)
        self.tabs.addTab(self.scan_tab, api.chosen_language.translate("tab_scan"))
        self.tabs.addTab(self.quarantine_tab, api.chosen_language.translate("tab_quarantine"))
        self.tabs.addTab(self.config_tab, api.chosen_language.translate("tab_configs"))
        self.tabs.addTab(self.about_tab, api.chosen_language.translate("tab_about"))
        for i in api._custom_tabs:
            self.tabs.addTab(i[0], i[1])
        self.tabs.currentChanged.connect(self.handle_tab_change)
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def handle_scan(self, mode, files):
        self.scan_type = mode
        self.scan_paths = files
        self.close()

    def handle_tab_change(self, index):
        if index == 1:
            self.quarantine_tab.populate_table()
        elif index == 2:
            self.config_tab.load_plugins()
