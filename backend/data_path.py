

class CheckDbPath:

    SELECT_DATA_MSG = 'Please select file data first!'
    DATA_SELECTED = 'Data path saved.'

    def __init__(self, lineedit, statusbar):
        self.line_edit = lineedit
        self.status_bar = statusbar

    def _is_lineedit_empty(self) -> bool:
        if len(self.line_edit.text()) == 0:
            return True
        else:
            return False
        
    def _display_status(self, message: str):
        return self.status_bar.showMessage(message, 5000)

    def _check_path(self, path: str):
        if path:
            self.line_edit.setText(path)
            self._display_status(self.DATA_SELECTED)
    
    def check(self, open_explorer):
        if self._is_lineedit_empty():
            self._display_status(self.SELECT_DATA_MSG)
        
        self._check_path(open_explorer())