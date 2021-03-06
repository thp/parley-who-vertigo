#
# Parley Who Vertigo
# Copyright 2016, 2017 Thomas Perl, Josef Who
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
#


import minigame
import psmovecolor
import moveplayer

from color import Color

class MoveSays(minigame.MiniGame):
    ENABLED = True

    def __init__(self, gameflow):
        super().__init__(gameflow)
        self.players_ready = 0
        self.players_remaining = 0

    def status_message(self):
        return 'Pressz se KOLOR!'

    def start_game(self):
        def on_intro_blinking_finished():
            self.players_ready += 1
            if self.players_ready == len(self.gameflow.players):
                for player in self.gameflow.players:
                    player.led_color = psmovecolor.PSMoveColor.get_random_color()
                self.players_remaining = self.players_ready

        for player in self.gameflow.players:
            parts = []
            for i in range(10):
                parts.append(moveplayer.AnimationPart(psmovecolor.PSMoveColor.get_random_color(), 0.1))
                parts.append(moveplayer.AnimationPart(Color.BLACK, 0.1))

            def on_changed():
                self.gameflow.play_sound('CycleBlipSound')

            self.gameflow.start_coroutine(player.sphere_color_animation(parts, on_intro_blinking_finished, on_changed))

    def button_pressed(self, player, button):
        if self.players_ready < len(self.gameflow.players):
            return

        if psmovecolor.PSMoveColor.is_color_button(button):
            color = psmovecolor.PSMoveColor.color_for_button(button)
            if color == player.led_color:
                self.gameflow.play_sound('BeepSound', 0.5)
                self.gameflow.end_current_game(player)
            elif player.led_color != Color.BLACK:
                self.gameflow.play_sound('BadBeepSound', 0.5)
                # TODO: Play "dead" animation
                player.led_color = Color.BLACK
                self.players_remaining -= 1
                if self.players_remaining == 0:
                    self.gameflow.end_current_game_no_winner()

    def base_color(self):
        return psmovecolor.PSMoveColor.get_random_color()

    def update(self):
        ...
