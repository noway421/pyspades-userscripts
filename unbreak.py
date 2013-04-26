"""
Set landshaft in some areas unbreakable

* Only users blocks can be breaked

You can configure locations for unbreaking in map file. Example:

unbreak = ['B6','B7','B8','C8','D8','E6','E7','E8'] # this squares unbreakable

or

unbreak = True # unbreakable whole map

or

unbreak = False # disable unbreakable

Maintainer: noway421
"""

from collections import namedtuple
from pyspades.color import rgb_distance
from pyspades.constants import *
from pyspades.common import coordinates

DIRT_COLOR = (71, 48, 35)
ALWAYS_ENABLED = False  # Ignore map overrides?


def apply_script(protocol, connection, config):
    class UnbreakConnection(connection):
        def on_disconnect(self):
            if bool(self.protocol.unbreak):
                player_blocks = self.protocol.player_blocks
                for xyz, player_block in player_blocks.iteritems():
                    if player_block[0] is self:
                        # mojno zagadit' mapu i uiti, nichego ne budet
                        player_blocks[xyz] = (None, )
            return connection.on_disconnect(self)

        def on_block_build(self, x, y, z):
            if bool(self.protocol.unbreak):
                if self.protocol.is_unbreak_area(x, y, z):
                    player_block = (self, )
                    self.protocol.player_blocks[(x, y, z)] = player_block
            return connection.on_block_build(self, x, y, z)

        def on_line_build(self, points):
            if bool(self.protocol.unbreak):
                player_block = (self, )
                for xyz in points:
                    if self.protocol.is_unbreak_area(xyz[0], xyz[1], xyz[2]):
                        self.protocol.player_blocks[xyz] = player_block
            return connection.on_line_build(self, points)

        def on_block_destroy(self, x, y, z, value):
            can_destroy = connection.on_block_destroy(self, x, y, z, value)
            if bool(self.protocol.unbreak):
                if self.protocol.is_unbreak_area(x, y, z):
                    if can_destroy is not False:
                        player_block = self.protocol.player_blocks.pop(
                            (x, y, z), None)
                        if player_block is None:
                            return False
            return can_destroy

    class UnbreakProtocol(protocol):
        player_blocks = None
        unbreak = False

        def on_map_change(self, map):
            info = self.map_info.info
            if ALWAYS_ENABLED:
                self.unbreak = True
            else:
                ubrk = getattr(info, 'unbreak', True)
                if ubrk is True or ubrk is False:
                    self.unbreak = ubrk
                else:
                    self.unbreak = set(coordinates(s) for s in ubrk)
            self.player_blocks = {}
            return protocol.on_map_change(self, map)

        def is_unbreak_area(self, x, y, z):
            if self.unbreak is True:
                return True
            if bool(self.unbreak):
                for sx, sy in self.unbreak:
                    if x >= sx and y >= sy and x < sx + 64 and y < sy + 64:
                        return True
            return False
    return UnbreakProtocol, UnbreakConnection
