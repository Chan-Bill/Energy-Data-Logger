from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog
from frontend.view import Ui_MainWindow

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from backend.model import LoggerModel, PandasModel
from backend.data_path import CheckDbPath

import os


class Household:
    def __init__(self, name: str, current_number_of_person: int):
        self.name = name
        self.current_number_of_person = current_number_of_person

    def get_name(self):
        return self.name
    
    def get_num_person(self):
        return self.current_number_of_person


class LoggerController:
    def __init__(self, model: LoggerModel) -> None:
        self.model = model

    def register_new_household(self, household_name: str, number_person: int) -> None:
        new_household = Household(household_name, number_person) 
        self.model.register_household(new_household)

    def delete_household(self, household_id: int) -> None:
        self.model.delete_household(household_id)

    def activate_household(self, active_household: dict) -> None:
        self.model.save_active_household(active_household)

    def get_registered_households(self) -> list:
        return self.model.get_registered_households()
    
    def get_household_id(self, household_name: str) -> int:
        return self.model.get_registered_household_id(household_name)
    
    def get_active_household(self) -> dict:
        return self.model.get_active_household()
    
    def get_all_sensor_data(self, household: str):
        return self.model.get_all_data(household)


class HouseholdView(QMainWindow, Ui_MainWindow):
    def __init__(self, model, controller):
        super().__init__()
        self.setupUi(self)

        self.model = model
        self.controller = controller

        self.dialog_widget = DialogWidgets()

        self.setup_connections()
        # self.setup_comboboxes()
        
        # self.setup_canvases()

        
        
    def setup_canvases(self):
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.horizontalLayout_10.addWidget(self.canvas)

    def register_household(self):
        household_name = self.lineEdit.text()

        if not household_name:
            self.show_error_message("Household name cannot be empty.")
            return
        
        try:
            self.controller.register_new_household(household_name, self.spinBox.value())
            self.update_comboboxes()
        except ValueError as e:
            self.show_error_message(str(e))

    def delete_household(self):
        household_id = self.lineEdit_4.text()
        self.controller.delete_household(household_id)
        self.update_comboboxes()
        self.update_active_household_lineedit()

    def activate_household(self):
        if self.lineEdit_5.text() != 'None' and self.comboBox_2.currentText() != '':
            active_household = {
                'id': self.lineEdit_5.text(),
                'name': self.comboBox_2.currentText(),
            }
            self.controller.activate_household(active_household)
            self.update_active_household_lineedit()

    def update_active_household_lineedit(self):
        saved_active_household = self.controller.get_active_household()
        if saved_active_household != None:
            self.lineEdit_2.setText(saved_active_household["name"])
        else:
            self.lineEdit_2.setText("")
            
    def display_all_visualization(self):
        self.display_data_log()
        self.display_linear_regression()
    
            
    def display_data_log(self):
        data = self.controller.get_all_sensor_data(household=self.comboBox.currentText())
        model = PandasModel(data)
        self.tableView.setModel(model)
        
    
        

    def update_comboboxes(self):
        self.setup_combobox(self.comboBox_2, self.lineEdit_5)
        self.setup_combobox(self.comboBox_3, self.lineEdit_4)
        self.setup_combobox(self.comboBox)

    def setup_connections(self):
        self.pushButton_3.clicked.connect(self.register_household)
        self.pushButton_4.clicked.connect(self.activate_household)
        self.pushButton_5.clicked.connect(self.delete_household)
        self.pushButton.clicked.connect(self.check_database_path)
        # self.pushButton.clicked.connect(self.display_all_visualization)
        

    def setup_comboboxes(self):
        self.setup_combobox(self.comboBox_2, self.lineEdit_5)
        self.setup_combobox(self.comboBox_3, self.lineEdit_4)
        self.setup_combobox(self.comboBox)

    def setup_combobox(self, combobox, related_lineedit = None):
        combobox.clear()
        items = self.controller.get_registered_households()
        combobox.addItems([item["name"] for item in items])

        if related_lineedit != None:
            self.handle_combobox_change(combobox, related_lineedit)
            combobox.currentIndexChanged.connect(lambda: self.handle_combobox_change(combobox, related_lineedit))

    def handle_combobox_change(self, combobox, related_lineedit):
        selected_text = combobox.currentText()
        try:
            household_id = str(self.controller.get_household_id(selected_text))
            related_lineedit.setText(household_id)
        except TypeError as e:
            print(str(e))

    def show_error_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.exec_()

    #------------------------------------------------------------------------------------
    def check_database_path(self):
        checker = CheckDbPath(self.lineEdit_6, self.statusbar)
        checker.check(self.dialog_widget.get_file_from_explorer)


class DialogWidgets(QMainWindow):

    def get_file_from_explorer(self):
        documents_path = os.path.expanduser('~/Documents')
        file_name = QFileDialog.getOpenFileName(self, 'Open file', documents_path)
        if file_name[0]:
            return file_name[0]
        else:
            return False


if __name__ == "__main__":
    def main():
        app = QApplication([])
        model = LoggerModel()
        controller = LoggerController(model)
        view = HouseholdView(model, controller)
        view.show()
        app.exec_()

    main()
