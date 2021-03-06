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


import psmoveapi
import moveplayer
import coroutine
import tunablevariables
import minigame

import random
import glob
import os
import importlib

from color import Color

from minigames import attractmode

class Counter(object):
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1

    def decrement(self):
        self.value -= 1
        return self.value == 0


def find_minigame_classes():
    """Find all Python classes that subclass minigame.MiniGame in minigames/"""
    for filename in glob.glob(os.path.join(os.path.dirname(__file__), 'minigames', '*.py')):
        bn = os.path.basename(filename)
        if bn == '__init__.py':
            continue

        modulename, _ = os.path.splitext(bn)
        module = importlib.import_module('minigames.' + modulename)
        for k, v in module.__dict__.items():
            if isinstance(v, type) and issubclass(v, minigame.MiniGame):
                yield (modulename, v)


class GameFlow(object):
    def __init__(self, main_script):
        self.main_script = main_script

        self.players = [moveplayer.MovePlayer(index, controller)
                        for index, controller in enumerate(self.main_script.get_controllers())]

        self.current_game = None
        self.remaining_games = 0
        self.current_message = '***'

        self.reset_game()

    def reset_game(self):
        self.remaining_games = self.get_tunables().DefaultNumberOfGames

        for player in self.players:
            player.score = 0

        self.current_game = attractmode.AttractMode(self)
        self.current_game.start_game()

    def everyone_is_ready(self):
        self.current_game = None
        self.select_new_game()

    def play_sound_delayed(self, sound, delay_sec):
        yield coroutine.WaitForSeconds(delay_sec)
        self.play_sound(sound)

    def select_new_game(self):
        # TODO: "New game starts sound"
        tunables = self.get_tunables()

        max_score = 0
        for player in self.players:
            player.led_color = Color.BLACK
            player.rumble = 0.0
            max_score = max(max_score, player.score)

        if self.remaining_games == 0:
            self.current_message = 'Session ** Ends'
            remaining_winners = Counter()

            self.start_coroutine(self.play_sound_delayed('GameWin2Sound', tunables.GameWinAnimationWaitBeforeSec))

            for player in self.players:
                def on_finished():
                    if remaining_winners.decrement():
                        self.reset_game()
                if max_score == player.score:
                    remaining_winners.increment()
                    self.start_coroutine(player.game_win_animation(tunables, on_finished))
        else:
            games = []

            for minigame_module, minigame_class in find_minigame_classes():
                is_enabled = getattr(minigame_class, 'ENABLED', True)
                if is_enabled:
                    print('Found minigame:', minigame_class)
                    games.append(minigame_class(self))
                else:
                    print('Minigame is disabled:', minigame_class)

            self.current_game = random.choice(games)
            self.current_game.start_game()
            self.remaining_games -= 1

    def update_controllers(self):
        for player in self.players:
            # Geht L2, L1, R1, ... (alle PSMoveButton-Werte) durch
            for button in psmoveapi.Button.VALUES:
                if player.is_button_pressed_now_and_not_before(button):
                    if self.current_game is not None:
                        self.current_game.button_pressed(player, button)

            player.update()

    def play_sound(self, sound, volume=1.0, pitch=1.0):
        self.main_script.play_sound(sound, volume, pitch)

    def update(self):
        self.update_controllers()

        if self.current_game is not None:
            self.current_game.update()

    def get_tunables(self):
        return tunablevariables.TunableVariables

    def end_current_game_no_winner(self):
        self.end_current_game()

    def end_current_game(self, *winners):
        if self.current_game is None:
            return

        # Disable access to "old" current game; new current game will be set by the winner player
        self.current_game = None

        for player in self.players:
            player.led_color = Color.BLACK

        if len(winners) == 0:
            # TODO: Play "nobody wins" sound/animation and wait a bit before new game
            self.current_message = 'Nobody wins...'
            self.select_new_game()
        else:
            winning_sounds = ['WinPlayer1Sound', 'WinPlayer2Sound']

            if len(winners) == 1:
                self.current_message = 'Player %d wins the round' % (winners[0].player_number + 1)
            else:
                self.current_message = 'Winners: Player ' + ' and '.join(str(w.player_number+1) for w in winners)

            self.play_sound(winning_sounds[winners[0].player_number % len(winning_sounds)], 0.2)

            def on_finished():
                self.select_new_game()

            for winner in winners:
                self.start_coroutine(winner.win_animation(self.get_tunables(), on_finished))
                winner.score += 1
                def on_finished():
                    ...  # Do nothing

    def start_coroutine(self, crt):
        self.main_script.start_coroutine(crt)

    def status_message(self):
        result = []
        if self.current_game is not None:
            result.append(self.current_game.__class__.__name__ if self.current_game else '-')
            result.append(self.current_game.status_message())
        else:
            result.append('Woop!')
            result.append(self.current_message)

        result.append(str(player.score) for player in self.players)

        return result
