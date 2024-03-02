from PyQt5.QtWidgets import QMainWindow, QApplication
from frontend.view import Ui_MainWindow

from backend.model import LoggerModel


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

        self.window_activate = ActivateTab(ui=self, controller=self.controller)
        self.window_activate.run()

        self.window_register = RegisterTab(ui=self, controller=self.controller)
        self.window_register.run()

        self.window_delete = RemoveTab(ui=self, controller=self.controller)
        self.window_delete.run()


class ComboboxUpdate:

    def __init__(self, comboboxes: list, controller) -> None:
        self.comboboxes = comboboxes
        self.controller = controller

    def update_combobox(self):
        for combo in self.comboboxes:
            combo.clear()
            items = self.controller.get_registered_households()
            combo.addItems([item["name"] for item in items])


class ActivateTab:

    def __init__(self, ui, controller):
        self.ui = ui
        self.controller = controller

    def run(self):
        self.setup_connections()
        self._update_lineedit_id()

    def setup_connections(self):
        self.setup_update_combobox()
        self.setup_lineedit()
        self.setup_save_button()
        self.setup_activate_button()

    def setup_update_combobox(self):
        combobox = ComboboxUpdate([self.ui.comboBox_2, self.ui.comboBox_3], self.controller)
        combobox.update_combobox()

    def setup_lineedit(self):
        self.ui.comboBox_2.currentIndexChanged.connect(self._update_lineedit_id)

    def _update_lineedit_id(self):
        selected_text = self.ui.comboBox_2.currentText()
        try:
            household_id = str(self.controller.get_household_id(selected_text))
            self.ui.lineEdit_5.setText(household_id)
        except TypeError as e:
            self.ui.status_bar.showMessage(str(e), 10000)

    def setup_save_button(self):
        self.ui.pushButton_4.clicked.connect(self._activate_household)

    def _activate_household(self):
        if self.ui.lineEdit_5.text() != 'None' and self.ui.comboBox_2.currentText() != '':
            active_household = {
                'id': self.ui.lineEdit_5.text(),
                'name': self.ui.comboBox_2.currentText(),
            }
            self.controller.activate_household(active_household)
            self._update_active_household_lineedit()

    def _update_active_household_lineedit(self):
        saved_active_household = self.controller.get_active_household()
        if saved_active_household != None:
            self.ui.lineEdit_2.setText(saved_active_household["name"])
        else:
            self.ui.lineEdit_2.setText("")

    def setup_activate_button(self):
        self.ui.pushButton.clicked.connect(self._switch_to_activate_tab)

    def _switch_to_activate_tab(self):
        self.ui.stackedWidget.setCurrentIndex(0)


class RegisterTab:

    def __init__(self, ui, controller):
        self.ui = ui
        self.controller = controller

    def run(self):
        self.setup_add_button()
        self.setup_register_button()

    def setup_add_button(self):
        self.ui.pushButton_3.clicked.connect(self._register_household)

    def _register_household(self):
        household_name = self.ui.lineEdit.text()

        if not household_name:
            self.ui.statusbar.showMessage("Household name cannot be empty.", 10000)
            return
        
        try:
            self.controller.register_new_household(household_name, self.ui.spinBox.value())
            self.setup_update_combobox()
        except ValueError as e:
            self.ui.statusbar.showMessage(str(e), 10000)

    def setup_update_combobox(self):
        combobox = ComboboxUpdate([self.ui.comboBox_2, self.ui.comboBox_3], self.controller)
        combobox.update_combobox()

    def setup_register_button(self):
        self.ui.pushButton_2.clicked.connect(self._switch_to_register_tab)

    def _switch_to_register_tab(self):
        self.ui.stackedWidget.setCurrentIndex(1)


class RemoveTab:

    def __init__(self, ui, controller):
        self.ui = ui
        self.controller = controller

    def run(self):
        self.setup_connection()
        self._update_lineedit_id()
        
    def setup_connection(self):
        self.ui.pushButton_5.clicked.connect(self.delete_household)
        self.setup_remove_button()
        self.setup_lineedit()

    def delete_household(self):
        household_id = self.ui.lineEdit_4.text()
        self.controller.delete_household(household_id)
        self.setup_update_combobox()
    
    def setup_lineedit(self):
        self.ui.comboBox_3.currentIndexChanged.connect(self._update_lineedit_id)

    def _update_lineedit_id(self):
        selected_text = self.ui.comboBox_3.currentText()
        try:
            household_id = str(self.controller.get_household_id(selected_text))
            self.ui.lineEdit_4.setText(household_id)
        except TypeError as e:
            self.ui.status_bar.showMessage(str(e), 10000)

    def setup_update_combobox(self):
        combobox = ComboboxUpdate([self.ui.comboBox_2, self.ui.comboBox_3], self.controller)
        combobox.update_combobox()

    def setup_remove_button(self):
        self.ui.pushButton_6.clicked.connect(self._switch_to_remove_tab)

    def _switch_to_remove_tab(self):
        self.ui.stackedWidget.setCurrentIndex(2)


if __name__ == "__main__":
    def main():
        app = QApplication([])
        model = LoggerModel()
        controller = LoggerController(model)
        view = HouseholdView(model, controller)
        view.show()
        app.exec_()

    main()
