import psmoveapi
import moveplayer
import coroutine
import color
import tunablevariables

import random


from minigame import attractmode
from minigame import movesays
from minigame import shakeit
from minigame import safecracker


class Counter(object):
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1

    def decrement(self):
        self.value -= 1
        return self.value == 0


class GameFlow(object):
    def __init__(self):
        count = psmoveapi.get_num_connected()  # TODO

        self.players = []

        player = 0
        for i in range(count):
            mp = moveplayer.MovePlayer(player)
            if mp.valid():
                player += 1
                self.players.append(mp)

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
            player.led_color = color.Color.BLACK
            player.rumble = 0.0
            max_score = max(max_score, player.score)

        print('Selecting new game')
        if self.remaining_games == 0:
            print('Session ends')
            self.current_message = 'Session ** Ends'
            remaining_winners = Counter()

            self.start_coroutine(self.play_sound_delayed('GameWin2Sound', tunables.GameWinAnimationWaitBeforeSec))

            for player in self.players:
                def on_finished():
                    print('on_finished called')
                    if remaining_winners.decrement():
                        self.reset_game()
                print('Player score:', player.score, ', max score:', max_score)
                if max_score == player.score:
                    remaining_winners.increment()
                    self.start_coroutine(player.game_win_animation(tunables, on_finished))
        else:
            games = []
            if tunables.EnableMoveSays:
                games.append(movesays.MoveSays(self))
            if tunables.EnableShakeIt:
                games.append(shakeit.ShakeIt(self))
            if tunables.EnableSafeCracker:
                games.append(safecracker.SafeCracker(self))

            self.current_game = random.choice(games)
            self.current_game.start_game()
            self.remaining_games -= 1

    def update_controllers(self):
        for player in self.players:
             # Geht L2, L1, R1, ... (alle PSMoveButton-Werte) durch
             for button in psmoveapi.Button.values():
                 if player.is_button_down(button):
                     if self.current_game is not None:
                         self.current_game.button_pressed(player, button)

            player.update()

    def play_sound(self, sound, volume=1.0, pitch=1.0):
        # TODO: Play sound at volume and pitch
        print('Would play sound:', sound)

    def update(self):
        self.update_controllers()

        if self.current_game is not None:
            self.current_game.update()

    def get_tunables(self):
        return tunablevariables.TunableVariables

    def end_current_game_no_winner(self):
        self._end_current_game()

    def end_current_game(self, *winners):
        if self.current_game is None:
            return

        # Disable access to "old" current game; new current game will be set by the winner player
        self.current_game = None

        print('Game ends, winner(s):', winners)

        for player in self.players:
            player.led_color = color.Color.BLACK

        if len(winners) == 0:
            # TODO: Play "nobody wins" sound/animation and wait a bit before new game
            self.select_new_game()
        else:
            winning_sounds = ['WinPlayer1Sound', 'WinPlayer2Sound']

            self.play_sound(winning_sounds[winners[0].player_number % len(winning_sounds), 0.2)

            def on_finished():
                self.select_new_game()

            for winner in winners:
                self.start_coroutine(winner.win_animation(self.get_tunables(), on_finished))
                winner.score += 1
                def on_finished():
                    ...  # Do nothing

    def start_coroutine(self, crt):
        print('Would run coroutine:', crt)  # TODO

    def status_message(self):
        result = ''
        if self.current_game is not None:
            result += 'current game: ' + self.current_game + '\n' + self.current_game.status_message()
        else:
            result += self.current_message

        result += '\n'

        for player in self.players:
            result += '\n'
            result == 'Player ' + (player.player_number + 1) + ': ' + player.score + ' points'

        return result
