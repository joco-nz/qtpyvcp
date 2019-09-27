#   Copyright (c) 2018 Kurt Jacobson
#      <kurtcjacobson@gmail.com>
#
#   This file is part of QtPyVCP.
#
#   QtPyVCP is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   QtPyVCP is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with QtPyVCP.  If not, see <http://www.gnu.org/licenses/>.

from qtpy.QtCore import Qt, Slot, Property, QModelIndex, QSortFilterProxyModel
from qtpy.QtGui import QStandardItemModel, QColor, QBrush
from qtpy.QtWidgets import QTableView, QStyledItemDelegate, QDoubleSpinBox, QSpinBox, QLineEdit, QMessageBox

from qtpyvcp.utilities.logger import getLogger
from qtpyvcp.plugins import getPlugin

LOG = getLogger(__name__)


class ItemDelegate(QStyledItemDelegate):

    def __init__(self, columns):
        super(ItemDelegate, self).__init__()

        self._columns = columns
        self._padding = ' ' * 2

    def setColumns(self, columns):
        self._columns = columns

    def displayText(self, value, locale):

        if type(value) == float:
            return "{0:.4f}".format(value)

        return "{}{}".format(self._padding, value)

    def createEditor(self, parent, option, index):
        # ToDo: set dec placed for IN and MM machines
        col = self._columns[index.column()]

        if col == 'R':
            editor = QLineEdit(parent)
            editor.setFrame(False)
            margins = editor.textMargins()
            padding = editor.fontMetrics().width(self._padding) + 1
            margins.setLeft(margins.left() + padding)
            editor.setTextMargins(margins)
            return editor

        elif col in 'TPQ':
            editor = QSpinBox(parent)
            editor.setFrame(False)
            editor.setAlignment(Qt.AlignCenter)
            if col == 'Q':
                editor.setMaximum(9)
            else:
                editor.setMaximum(99999)
            return editor

        elif col in 'XYZABCUVWD':
            editor = QDoubleSpinBox(parent)
            editor.setFrame(False)
            editor.setAlignment(Qt.AlignCenter)
            editor.setDecimals(4)
            # editor.setStepType(QSpinBox.AdaptiveDecimalStepType)
            editor.setProperty('stepType', 1)  # stepType was added in 5.12
            editor.setRange(-1000, 1000)
            return editor

        elif col in 'IJ':
            editor = QDoubleSpinBox(parent)
            editor.setFrame(False)
            editor.setAlignment(Qt.AlignCenter)
            editor.setDecimals(2)
            # editor.setStepType(QSpinBox.AdaptiveDecimalStepType)
            editor.setProperty('stepType', 1)  # stepType was added in 5.12
            return editor

        return None


class OffsetModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(OffsetModel, self).__init__(parent)

        self.status = getPlugin('status')
        self.stat = self.status.stat
        self.ot = getPlugin('offsettable')

        self.current_row_color = QColor(Qt.darkGreen)

        self._columns = self.ot.columns
        self._column_labels = self.ot.COLUMN_LABELS

        self._offset_table = self.ot.getOffsetTable()

        self.setColumnCount(self.columnCount())
        self.setRowCount(9)  # (self.rowCount())

        # self.status.tool_in_spindle.notify(self.refreshModel)
        # self.ot.tool_table_changed.connect(self.updateModel)

    def refreshModel(self):
        # refresh model so current row gets highlighted
        self.beginResetModel()
        self.endResetModel()

    def updateModel(self, offset_table):
        # update model with new data
        self.beginResetModel()
        self._offset_table = offset_table
        self.endResetModel()

    def setColumns(self, columns):
        self._columns = columns
        self.setColumnCount(len(columns))

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._column_labels[self._columns[section]]

        return QStandardItemModel.headerData(self, section, orientation, role)

    def columnCount(self, parent=None):
        return len(self._columns)

    def rowCount(self, parent=None):
        return len(self._offset_table) - 1

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            key = self._columns[index.column()]
            tnum = sorted(self._offset_table)[index.row() + 1]
            return self._offset_table[tnum][key]

        elif role == Qt.TextAlignmentRole:
            col = self._columns[index.column()]
            if col == 'R':  # Remark
                return Qt.AlignVCenter | Qt.AlignLeft
            elif col in 'TPQ':  # Integers (Tool, Pocket, Orient)
                return Qt.AlignVCenter | Qt.AlignCenter
            else:  # All the other floats
                return Qt.AlignVCenter | Qt.AlignRight

        elif role == Qt.TextColorRole:
            tnum = sorted(self._offset_table)[index.row() + 1]
            if self.stat.tool_in_spindle == tnum:
                return QBrush(self.current_row_color)
            else:
                return QStandardItemModel.data(self, index, role)

        return QStandardItemModel.data(self, index, role)

    def setData(self, index, value, role):
        key = self._columns[index.column()]
        tnum = sorted(self._offset_table)[index.row() + 1]
        self._offset_table[tnum][key] = value
        return True

    def removeOffset(self, row):
        self.beginRemoveRows(QModelIndex(), row, row)
        tnum = sorted(self._offset_table)[row + 1]
        del self._offset_table[tnum]
        self.endRemoveRows()
        return True

    def addOffset(self):
        try:
            tnum = sorted(self._offset_table)[-1] + 1
        except IndexError:
            tnum = 1

        row = len(self._offset_table) - 1

        if row == 9:
            # max 9 tools
            return False

        self.beginInsertRows(QModelIndex(), row, row)
        self._offset_table[tnum] = self.ot.newOffset(tnum=tnum)
        self.endInsertRows()
        return True

    def offsetDataFromRow(self, row):
        o_num = sorted(self._offset_table)[row]
        return self._offset_table[o_num]

    def saveOffsetTable(self):
        self.ot.saveOffsetTable(self._offset_table)
        return True

    def clearOffsetTable(self):
        self.beginRemoveRows(QModelIndex(), 0, 100)
        # delete all but the spindle, which can't be deleted
        self._offset_table = {0: self._offset_table[0]}
        self.endRemoveRows()
        return True

    def loadOffsetTable(self):
        # the tooltable plugin will emit the tool_table_changed signal
        # so we don't need to do any more here
        self.ot.loadOffsetTable()
        return True


class OffsetTable(QTableView):
    def __init__(self, parent=None):
        super(OffsetTable, self).__init__(parent)

        self.offset_model = OffsetModel(self)

        self.item_delegate = ItemDelegate(columns=self.offset_model._columns)
        self.setItemDelegate(self.item_delegate)

        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setFilterKeyColumn(0)
        self.proxy_model.setSourceModel(self.offset_model)

        self.setModel(self.proxy_model)

        # Properties
        self._columns = self.offset_model._columns
        self._confirm_actions = False
        self._current_row_color = QColor('sage')

        # Appearance/Behaviour settings
        self.setSortingEnabled(True)
        # self.verticalHeader().hide()
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSortIndicator(0, Qt.AscendingOrder)

    @Slot()
    def saveOffsetTable(self):
        if not self.confirmAction("Do you want to save changes and\n"
                                  "load tool table into LinuxCNC?"):
            return
        self.offset_model.saveOffsetTable()

    @Slot()
    def loadOffsetTable(self):
        if not self.confirmAction("Do you want to re-load the tool table?\n"
                                  "All unsaved changes will be lost."):
            return
        self.offset_model.loadOffsetTable()

    @Slot()
    def deleteSelectedOffset(self):
        """Delete the currently selected item"""
        current_row = self.selectedRow()
        if current_row == -1:
            # no row selected
            return

        odata = self.offset_model.offsetDataFromRow(current_row)
        if not self.confirmAction("Are you sure you want to delete offset {odata[T]}?\n"
                                  "{odata[R]}".format(tdata=odata)):
            return

        self.offset_model.removeOffset(current_row)

    @Slot()
    def selectPrevious(self):
        """Select the previous item in the view."""
        self.selectRow(self.selectedRow() - 1)
        return True

    @Slot()
    def selectNext(self):
        """Select the next item in the view."""
        self.selectRow(self.selectedRow() + 1)
        return True

    @Slot()
    def clearOffsetTable(self, confirm=True):
        """Remove all items from the model"""
        if confirm:
            if not self.confirmAction("Do you want to delete the whole offsets table?"):
                return

        self.offset_model.clearOffsetTable()

    def selectedRow(self):
        """Returns the row number of the currently selected row, or 0"""
        return self.selectionModel().currentIndex().row()

    def confirmAction(self, message):
        if not self._confirm_actions:
            return True

        box = QMessageBox.question(self,
                                   'Confirm Action',
                                   message,
                                   QMessageBox.Yes,
                                   QMessageBox.No)
        if box == QMessageBox.Yes:
            return True
        else:
            return False

    @Property(str)
    def displayColumns(self):
        return "".join(self._columns)

    @displayColumns.setter
    def displayColumns(self, columns):
        self._columns = [col for col in columns.upper() if col in 'TPXYZABCUVWDIJQR']
        self.offset_model.setColumns(self._columns)
        self.itemDelegate().setColumns(self._columns)

    @Property(bool)
    def confirmActions(self):
        return self._confirm_actions

    @confirmActions.setter
    def confirmActions(self, confirm):
        self._confirm_actions = confirm

    @Property(QColor)
    def currentRowColor(self):
        return self.offset_model.current_row_color

    @currentRowColor.setter
    def currentRowColor(self, color):
        self.offset_model.current_row_color = color
