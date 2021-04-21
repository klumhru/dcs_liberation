from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from game import db
from game.theater import ControlPoint
from game.transfers import Convoy
from qt_ui.dialogs import Dialog
from qt_ui.models import GameModel
from qt_ui.uiconstants import VEHICLES_ICONS


class DepartingConvoyInfo(QGroupBox):
    def __init__(self, convoy: Convoy, game_model: GameModel) -> None:
        super().__init__(f"{convoy.name} to {convoy.destination}")
        self.convoy = convoy

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        unit_layout = QGridLayout()
        main_layout.addLayout(unit_layout)

        for idx, (unit_type, count) in enumerate(convoy.units.items()):
            icon = QLabel()
            if unit_type.id in VEHICLES_ICONS.keys():
                icon.setPixmap(VEHICLES_ICONS[unit_type.id])
            else:
                icon.setText("<b>" + unit_type.id[:8] + "</b>")
            icon.setProperty("style", "icon-armor")
            unit_layout.addWidget(icon, idx, 0)
            unit_display_name = db.unit_get_expanded_info(
                game_model.game.enemy_country, unit_type, "name"
            )
            unit_layout.addWidget(
                QLabel(f"{count} x <strong>{unit_display_name}</strong>"),
                idx,
                1,
            )

        if not convoy.units:
            unit_layout.addWidget(QLabel("/"), 0, 0)

        attack_button = QPushButton("Attack")
        attack_button.setProperty("style", "btn-danger")
        attack_button.setMaximumWidth(180)
        attack_button.clicked.connect(self.on_attack)
        main_layout.addWidget(attack_button, 0, Qt.AlignLeft)

    def on_attack(self):
        # TODO: Maintain Convoy list in Game.
        # The fact that we create these here makes some of the other bookkeeping
        # complicated. We could instead generate this at the start of the turn (and
        # update whenever transfers are created or canceled) and also use that time to
        # precalculate things like the next stop and group names.
        Dialog.open_new_package_dialog(self.convoy, parent=self.window())


class DepartingConvoysList(QFrame):
    def __init__(self, cp: ControlPoint, game_model: GameModel):
        super().__init__()
        self.cp = cp
        self.game_model = game_model
        self.setMinimumWidth(500)

        layout = QVBoxLayout()
        self.setLayout(layout)

        scroll_content = QWidget()
        task_box_layout = QGridLayout()
        scroll_content.setLayout(task_box_layout)

        convoy_map = game_model.game.transfers.convoys
        for convoy in convoy_map.departing_from(cp):
            group_info = DepartingConvoyInfo(convoy, game_model)
            task_box_layout.addWidget(group_info)

        scroll_content.setLayout(task_box_layout)
        scroll = QScrollArea()
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)


class DepartingConvoysMenu(QFrame):
    def __init__(self, cp: ControlPoint, game_model: GameModel):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(DepartingConvoysList(cp, game_model))
        self.setLayout(layout)
