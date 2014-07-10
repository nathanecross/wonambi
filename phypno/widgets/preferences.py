"""Large and simple widget to indicate settings/preferences.

"""
from logging import getLogger
lg = getLogger(__name__)

from PyQt4.QtCore import QSettings, Qt
from PyQt4.QtGui import (QCheckBox,
                         QDialog,
                         QFormLayout,
                         QGroupBox,
                         QHBoxLayout,
                         QLineEdit,
                         QPushButton,
                         QVBoxLayout,
                         QWidget,
                         )

config = QSettings("phypno", "scroll_data")


OLD_DEFAULTS = {'main/geometry': [400, 300, 1024, 768],
            'main/hidden_docks': ['Video'],
            'main/recording_dir': '/home/gio/recordings',
            'overview/window_start': 0,
            'overview/window_length': 30,
            'overview/window_length_presets': [1, 5, 10, 20, 30, 60],
            'overview/window_step': 5,
            'overview/timestamp_steps': 60 * 60,
            'traces/n_time_labels': 3,
            'traces/y_distance': 50.,
            'traces/y_distance_presets': [20, 30, 40, 50, 100, 200],
            'traces/y_scale': 1.,
            'traces/y_scale_presets': [.1, .2, .5, 1, 2, 5, 10],
            'traces/label_ratio': 0.05,
            'utils/read_intervals': 10 * 60,
            'stages/scoring_window': 30,
            'detect/spindle_method': 'UCSD',
            'video/vlc_size': '640x480',
            'video/vlc_exe': 'C:/Program Files (x86)/VideoLAN/VLC/vlc.exe',
            }


DEFAULTS = {}
DEFAULTS['spectrum'] = {'x_min': 0,
                        'x_max': 30,
                        'x_tick': 10,
                        'y_min': -5,
                        'y_max': 5,
                        'y_tick': 5,
                        'log': True,
                        }
DEFAULTS['utils'] = {'max_recording_history': 20,
                     }


"""


# Read/write default values using QSettings
for key, value in DEFAULTS.items():
    type_value = type(value)
    config_value = config.value(key)
    if config_value is not None:
        if type_value is list:
            DEFAULTS[key] = eval(config_value)
        else:
            DEFAULTS[key] = type_value(config_value)

class Preferences(QDialog):
    \"""Dialog which contains the preferences/settings.

    Attributes
    ----------
    parent : instance of QMainWindow
        The main window.
    values : dict
        Values of the preferences in key/value format.
    idx_edits : dict of instances of QLineEdit
        Values as QLineEdit for each preference value.

    \"""
    def __init__(self, parent):
        lg.debug('make preferences')
        super().__init__()
        self.parent = parent

        self.values = DEFAULTS

        self.idx_edits = {}

        self.create_preferences()

    def create_preferences(self):
        \"""Create the widgets containing the QLineEdit.\"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        group = {}
        group_layout = {}
        widgets = set([x.split('/')[0] for x in DEFAULTS])

        # It creates a QGroupBox with QFormLayout for each widget
        for one_widget in sorted(widgets):
            lg.debug('Adding preferences for ' + one_widget + ' widget')
            group[one_widget] = QGroupBox(one_widget)
            group_layout[one_widget] = QFormLayout()
            group[one_widget].setLayout(group_layout[one_widget])
            layout.addWidget(group[one_widget])

        # It adds row to a widget's QGroupBox
        for widget_key in sorted(DEFAULTS):
            one_widget, key = widget_key.split('/')
            edit = QLineEdit('')
            group_layout[one_widget].addRow(key, edit)
            self.idx_edits[widget_key] = edit

        ok_button = QPushButton('OK')
        ok_button.setAutoDefault(True)
        ok_button.clicked.connect(self.save_values)

        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def update_preferences(self):
        \"""Call directly display_preferences.

        Notes
        -----
        Usually, self.values should be None and values are updated here but in
        the case of preferences they should be available as soon as the
        widgets are created.

        \"""
        self.display_preferences()

    def display_preferences(self):
        \"""Display the preferences.\"""
        for widget_key, value in DEFAULTS.items():
            lg.debug('Setting {} to {}'.format(widget_key, value))
            self.idx_edits[widget_key].setText(str(value))

    def save_values(self):
        \"""Save edited values into QSettings file.

        Notes
        -----
        TODO: depending on the edit, update the figure.

        \"""
        for key, one_edit in self.idx_edits.items():
            text = one_edit.text()
            if text != self.values[key]:
                lg.info('Value has been modified: ' +
                        '{} -> {}'.format(self.values[key], text))
                self.values[key] = text
                config.setValue(key, text)

        self.accept()
"""

from PyQt4.QtGui import QDialogButtonBox, QStackedWidget, QSplitter, QListWidget

class REMOVEPreferences():
    def __init__(self, parent):
        self.values = OLD_DEFAULTS  # TODO: remove


class Preferences(QDialog):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.create_preferences()

    def create_preferences(self):
        bbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Apply
                                | QDialogButtonBox.Cancel)
        self.idx_ok = bbox.button(QDialogButtonBox.Ok)
        self.idx_apply = bbox.button(QDialogButtonBox.Apply)
        self.idx_cancel = bbox.button(QDialogButtonBox.Cancel)
        bbox.clicked.connect(self.button_clicked)

        page_list = QListWidget()
        page_list.setSpacing(1)
        page_list.currentRowChanged.connect(self.change_widget)

        pages = ['General', 'Spectrum']
        for one_page in pages:
            page_list.addItem(one_page)

        self.stacked = QStackedWidget()
        self.stacked.addWidget(self.parent.config)
        self.stacked.addWidget(self.parent.spectrum.config)

        hsplitter = QSplitter()
        hsplitter.addWidget(page_list)
        hsplitter.addWidget(self.stacked)

        btnlayout = QHBoxLayout()
        btnlayout.addStretch(1)
        btnlayout.addWidget(bbox)

        vlayout = QVBoxLayout()
        vlayout.addWidget(hsplitter)
        vlayout.addLayout(btnlayout)

        self.setLayout(vlayout)

    def change_widget(self, new_row):
        self.stacked.setCurrentIndex(new_row)

    def button_clicked(self, button):
        if button in (self.idx_ok, self.idx_apply):
            self.parent.spectrum.config.get_values()
            self.parent.spectrum.config.update_widget()

            if button == self.idx_ok:
                self.accept()

        if button == self.idx_cancel:
            self.reject()


    def update_preferences(self):
        # it should update the single widgets
        pass


def get_float(widget, default):
    """Get float from widget.

    Parameters
    ----------
    widget : instance of widget
        widget that has the getText method
    default : float
        default value for the parameter

    Returns
    -------
    float
        the value in text or default

    """
    text = widget.text()
    try:
        text = float(text)
    except ValueError:
        lg.debug('Cannot convert "' + str(text) + '" to float.' +
                 'Using default ' + str(default))
        text = default
    return text


class Config(QWidget):
    """You'll need to implement one methods:
        - create_config with the QGroupBox and layouts

    """
    def __init__(self, widget, update_widget):
        super().__init__()

        self.widget = widget
        value_names = list(DEFAULTS[widget].keys())

        self.value = self.create_values(value_names)
        self.index = self.create_indices(value_names)

        # I'm surprised this works, it calls the overloaded method already
        self.create_config()
        self.set_values()
        self.update_widget = update_widget

    def create_values(self, value_names):
        # it should read the preferences
        output = {}
        for one_value_name in value_names:
            output[one_value_name] = DEFAULTS[self.widget][one_value_name]

        return output

    def create_indices(self, value_names):
        # default to None as long as we don't have an index
        return dict(zip(value_names, [None] * len(value_names)))

    def get_values(self):
        # GET VALUES FROM THE GUI
        # TODO: save to preferences
        for value_name, widget in self.index.items():
            if isinstance(widget, QCheckBox):
                self.value[value_name] = widget.checkState() == Qt.Checked

            if isinstance(widget, QLineEdit):
                self.value[value_name] = get_float(widget,
                                                   self.value[value_name])

        # update values in case some values were not acceptable
        self.set_values()
        # call the function from parent widget
        self.update_widget()

    def set_values(self):
        # SET VALUES TO THE GUI
        for value_name, widget in self.index.items():
            if isinstance(widget, QCheckBox):
                if self.value[value_name]:
                    widget.setCheckState(Qt.Checked)
                else:
                    widget.setCheckState(Qt.Unchecked)

            if isinstance(widget, QLineEdit):
                widget.setText(str(self.value[value_name]))

    def create_config(self):
        # TO BE OVERLOAD
        pass
