from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

from dcs import Mission
from dcs.ships import Bulker_Handy_Wind
from dcs.unitgroup import ShipGroup

from game.transfers import CargoShip
from game.unitmap import UnitMap
from game.utils import knots

if TYPE_CHECKING:
    from game import Game


class CargoShipGenerator:
    def __init__(self, mission: Mission, game: Game, unit_map: UnitMap) -> None:
        self.mission = mission
        self.game = game
        self.unit_map = unit_map
        self.count = itertools.count()

    def generate(self) -> None:
        # Reset the count to make generation deterministic.
        for ship in self.game.transfers.cargo_ships:
            self.generate_cargo_ship(ship)

    def generate_cargo_ship(self, ship: CargoShip) -> ShipGroup:
        country = self.mission.country(
            self.game.player_country if ship.player_owned else self.game.enemy_country
        )
        waypoints = ship.route
        group = self.mission.ship_group(
            country,
            ship.name,
            Bulker_Handy_Wind,
            position=waypoints[0],
            group_size=1,
        )
        for waypoint in waypoints[1:]:
            # 12 knots is very slow but it's also nearly the max allowed by DCS for this
            # type of ship.
            group.add_waypoint(waypoint, speed=knots(12).kph)
        self.unit_map.add_cargo_ship(group, ship)
        return group
