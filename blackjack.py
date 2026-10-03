import os
import random
import subprocess
import tkinter as tk


class Card:

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    @property
    def value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11
        return int(self.rank)

    @property
    def color(self):
        return '#D32F2F' if self.suit in ['♥', '♦'] else '#212121'

    def __str__(self):
        return f'{self.rank}{self.suit}'


class Hand:

    def __init__(self, bet=10):
        self.cards = []
        self.bet = bet
        self.is_doubled = False

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        val = sum(c.value for c in self.cards)
        aces = sum(1 for c in self.cards if c.rank == 'A')
        while val > 21 and aces > 0:
            val -= 10
            aces -= 1
        return val

    def is_splittable(self):
        return len(self.cards) == 2 and (
            self.cards[0].value == self.cards[1].value
        )


class BlackjackGUI:

    def __init__(self, root):
        self.root = root
        self.root.title('Blackjack Casino')
        self.root.geometry('720x640')
        self.root.configure(bg='#0B4726')  # Dark green casino felt
# Set Window Title
        self.root.title("Blackjack Casino")

        # Set Window Icon
        icon_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "icon.png"
        )
        if os.path.exists(icon_path):
            try:
                # Load PNG icon and set it as the window icon
                self.icon_img = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(False, self.icon_img)
            except Exception as e:
                print(f"Could not load window icon: {e}")
        self.bankroll = 500
        self.base_bet = 10
        self.deck = []
        self.player_hands = []
        self.current_hand_idx = 0
        self.dealer_hand = Hand()

        self.load_sounds()
        self.setup_ui()
        self.start_new_round()

    def load_sounds(self):
        self.sounds = {}
        self.use_pygame_mixer = False
        base_dir = os.path.dirname(os.path.abspath(__file__))

        try:
            import pygame

            pygame.mixer.init()
            self.use_pygame_mixer = True
        except Exception:
            pass

        sound_files = {
            'deal': 'card_flip.wav',
            'win': 'win.wav',
            'bust': 'bust.wav',
        }
        for name, filename in sound_files.items():
            filepath = os.path.join(base_dir, filename)
            if os.path.exists(filepath):
                if self.use_pygame_mixer:
                    try:
                        import pygame

                        self.sounds[name] = pygame.mixer.Sound(filepath)
                    except Exception:
                        self.sounds[name] = None
                else:
                    self.sounds[name] = filepath
            else:
                self.sounds[name] = None

    def play_sound(self, name):
        sound = self.sounds.get(name)
        if not sound:
            return
        if self.use_pygame_mixer:
            sound.play()
        else:
            try:
                subprocess.Popen(['paplay', sound])
            except FileNotFoundError:
                try:
                    subprocess.Popen(['aplay', sound])
                except Exception:
                    pass

    def setup_ui(self):
        # Header Bar
        self.top_bar = tk.Frame(self.root, bg='#072F19', pady=10)
        self.top_bar.pack(fill='x')

        self.lbl_bankroll = tk.Label(
            self.top_bar,
            text=f'BANKROLL: ${self.bankroll}',
            font=('Helvetica', 14, 'bold'),
            fg='#FFD700',
            bg='#072F19',
        )
        self.lbl_bankroll.pack(side='left', padx=20)

        self.lbl_status = tk.Label(
            self.top_bar,
            text='Place your bet & deal!',
            font=('Helvetica', 12, 'italic'),
            fg='#FFFFFF',
            bg='#072F19',
        )
        self.lbl_status.pack(side='right', padx=20)

        # Table Area
        self.table_frame = tk.Frame(self.root, bg='#0B4726')
        self.table_frame.pack(expand=True, fill='both', padx=20, pady=10)

        # Dealer Section
        self.dealer_box = tk.LabelFrame(
            self.table_frame,
            text=' DEALER ',
            font=('Helvetica', 11, 'bold'),
            fg='#FFD700',
            bg='#0B4726',
            bd=2,
            relief='groove',
        )
        self.dealer_box.pack(fill='x', pady=10)

        self.dealer_cards_frame = tk.Frame(self.dealer_box, bg='#0B4726')
        self.dealer_cards_frame.pack(pady=10)

        # Player Section
        self.player_box = tk.LabelFrame(
            self.table_frame,
            text=' PLAYER ',
            font=('Helvetica', 11, 'bold'),
            fg='#FFD700',
            bg='#0B4726',
            bd=2,
            relief='groove',
        )
        self.player_box.pack(fill='x', pady=10)

        self.player_cards_frame = tk.Frame(self.player_box, bg='#0B4726')
        self.player_cards_frame.pack(pady=10)

        # In-Window Outcome Banner (Replaces Popups)
        self.lbl_result = tk.Label(
            self.table_frame,
            text='',
            font=('Helvetica', 13, 'bold'),
            fg='#FFD700',
            bg='#0B4726',
            pady=10,
        )
        self.lbl_result.pack(fill='x')

        # Bottom Controls
        self.controls_frame = tk.Frame(self.root, bg='#072F19', pady=15)
        self.controls_frame.pack(fill='x')

        btn_style = {
            'font': ('Helvetica', 11, 'bold'),
            'width': 10,
            'height': 1,
            'bd': 0,
            'cursor': 'hand2',
        }

        self.btn_hit = tk.Button(
            self.controls_frame,
            text='HIT',
            bg='#2E7D32',
            fg='white',
            activebackground='#1B5E20',
            command=self.hit,
            **btn_style,
        )
        self.btn_hit.grid(row=0, column=0, padx=8)

        self.btn_stand = tk.Button(
            self.controls_frame,
            text='STAND',
            bg='#C62828',
            fg='white',
            activebackground='#8E0000',
            command=self.stand,
            **btn_style,
        )
        self.btn_stand.grid(row=0, column=1, padx=8)

        self.btn_double = tk.Button(
            self.controls_frame,
            text='DOUBLE',
            bg='#F57F17',
            fg='white',
            activebackground='#FBC02D',
            command=self.double_down,
            **btn_style,
        )
        self.btn_double.grid(row=0, column=2, padx=8)

        self.btn_split = tk.Button(
            self.controls_frame,
            text='SPLIT',
            bg='#1565C0',
            fg='white',
            activebackground='#0D47A1',
            command=self.split_hand,
            **btn_style,
        )
        self.btn_split.grid(row=0, column=3, padx=8)

        self.btn_deal = tk.Button(
            self.controls_frame,
            text='DEAL',
            bg='#FFD700',
            fg='#000000',
            activebackground='#FFECB3',
            command=self.start_new_round,
            **btn_style,
        )
        self.btn_deal.grid(row=0, column=4, padx=8)

        self.controls_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)

    def create_card_widget(self, parent, card=None, is_hidden=False):
        card_frame = tk.Frame(
            parent,
            bg='#FFFFFF' if not is_hidden else '#1A237E',
            bd=2,
            relief='raised',
            width=65,
            height=90,
        )
        card_frame.pack_propagate(False)

        if is_hidden:
            lbl = tk.Label(
                card_frame,
                text='🂠',
                font=('Helvetica', 32),
                fg='#9FA8DA',
                bg='#1A237E',
            )
            lbl.pack(expand=True)
        else:
            lbl_rank = tk.Label(
                card_frame,
                text=card.rank,
                font=('Helvetica', 12, 'bold'),
                fg=card.color,
                bg='#FFFFFF',
            )
            lbl_rank.pack(anchor='nw', padx=3, pady=1)

            lbl_suit = tk.Label(
                card_frame,
                text=card.suit,
                font=('Helvetica', 22),
                fg=card.color,
                bg='#FFFFFF',
            )
            lbl_suit.pack(expand=True)

        return card_frame

    def reset_deck(self):
        suits = ['♠', '♥', '♦', '♣']
        ranks = [
            '2',
            '3',
            '4',
            '5',
            '6',
            '7',
            '8',
            '9',
            '10',
            'J',
            'Q',
            'K',
            'A',
        ]
        self.deck = [Card(s, r) for s in suits for r in ranks]
        random.shuffle(self.deck)

    def deal_card(self):
        if len(self.deck) < 10:
            self.reset_deck()
        self.play_sound('deal')
        return self.deck.pop()

    def start_new_round(self):
        if self.bankroll < self.base_bet:
            self.lbl_status.config(text='OUT OF CHIPS')
            return

        self.lbl_result.config(text='')  # Clear previous result
        self.reset_deck()
        self.player_hands = [Hand(bet=self.base_bet)]
        self.current_hand_idx = 0
        self.dealer_hand = Hand()

        for _ in range(2):
            self.player_hands[0].add_card(self.deal_card())
            self.dealer_hand.add_card(self.deal_card())

        self.btn_deal.config(state='disabled')
        self.btn_hit.config(state='normal')
        self.btn_stand.config(state='normal')

        self.lbl_status.config(text='Hit or Stand')
        self.update_ui()

    def current_hand(self):
        return self.player_hands[self.current_hand_idx]

    def render_hand_widgets(self, parent_frame, cards, hide_second=False):
        for widget in parent_frame.winfo_children():
            widget.destroy()

        for i, card in enumerate(cards):
            hidden = hide_second and i == 1
            card_widget = self.create_card_widget(
                parent_frame, card, is_hidden=hidden
            )
            card_widget.pack(side='left', padx=5)

    def update_ui(self):
        cur_hand = self.current_hand()

        can_double = (
            len(cur_hand.cards) == 2
            and not cur_hand.is_doubled
            and self.bankroll >= cur_hand.bet * 2
        )
        can_split = (
            cur_hand.is_splittable()
            and len(self.player_hands) == 1
            and self.bankroll >= cur_hand.bet * 2
        )

        self.btn_double.config(
            state='normal' if can_double else 'disabled'
        )
        self.btn_split.config(state='normal' if can_split else 'disabled')

        # Dealer Cards
        self.render_hand_widgets(
            self.dealer_cards_frame, self.dealer_hand.cards, hide_second=True
        )

        # Player Cards
        for widget in self.player_cards_frame.winfo_children():
            widget.destroy()

        for i, hand in enumerate(self.player_hands):
            hand_container = tk.Frame(
                self.player_cards_frame,
                bg='#0B4726',
                bd=1,
                relief='solid' if i == self.current_hand_idx else 'flat',
            )
            hand_container.pack(side='left', padx=15, pady=5)

            cards_subframe = tk.Frame(hand_container, bg='#0B4726')
            cards_subframe.pack()
            self.render_hand_widgets(cards_subframe, hand.cards)

            score_text = (
                f'Hand {i+1} (${hand.bet}) | Val: {hand.get_value()}'
            )
            if i == self.current_hand_idx and len(self.player_hands) > 1:
                score_text += ' ◄'

            lbl_hand_info = tk.Label(
                hand_container,
                text=score_text,
                font=('Helvetica', 10, 'bold'),
                fg='#FFD700' if i == self.current_hand_idx else '#CCCCCC',
                bg='#0B4726',
            )
            lbl_hand_info.pack(pady=4)

        self.lbl_bankroll.config(text=f'BANKROLL: ${self.bankroll}')

    def hit(self):
        hand = self.current_hand()
        hand.add_card(self.deal_card())

        if hand.get_value() >= 21:
            self.advance_hand()
        else:
            self.update_ui()

    def double_down(self):
        hand = self.current_hand()
        hand.bet *= 2
        hand.is_doubled = True
        hand.add_card(self.deal_card())
        self.advance_hand()

    def split_hand(self):
        hand = self.current_hand()
        h1 = Hand(bet=hand.bet)
        h2 = Hand(bet=hand.bet)

        h1.add_card(hand.cards[0])
        h2.add_card(hand.cards[1])

        h1.add_card(self.deal_card())
        h2.add_card(self.deal_card())

        self.player_hands = [h1, h2]
        self.current_hand_idx = 0
        self.update_ui()

    def advance_hand(self):
        if self.current_hand_idx < len(self.player_hands) - 1:
            self.current_hand_idx += 1
            self.update_ui()
        else:
            self.dealer_turn()

    def stand(self):
        self.advance_hand()

    def dealer_turn(self):
        self.btn_hit.config(state='disabled')
        self.btn_stand.config(state='disabled')
        self.btn_double.config(state='disabled')
        self.btn_split.config(state='disabled')

        self.render_hand_widgets(
            self.dealer_cards_frame, self.dealer_hand.cards, hide_second=False
        )

        while self.dealer_hand.get_value() < 17:
            self.dealer_hand.add_card(self.deal_card())
            self.render_hand_widgets(
                self.dealer_cards_frame,
                self.dealer_hand.cards,
                hide_second=False,
            )

        self.evaluate_payouts()

    def evaluate_payouts(self):
        d_val = self.dealer_hand.get_value()
        results = []

        for i, hand in enumerate(self.player_hands):
            p_val = hand.get_value()
            bet = hand.bet

            if p_val > 21:
                self.bankroll -= bet
                res = 'Bust (Lost)'
                self.play_sound('bust')
            elif d_val > 21 or p_val > d_val:
                self.bankroll += bet
                res = f'Win (+${bet})'
                self.play_sound('win')
            elif p_val < d_val:
                self.bankroll -= bet
                res = f'Loss (-${bet})'
            else:
                res = 'Push (Tie)'

            if len(self.player_hands) > 1:
                results.append(f'Hand {i+1}: {res}')
            else:
                results.append(f'{res}')

        outcome_text = '  |  '.join(results)
        self.lbl_result.config(text=f'Dealer: {d_val}  ►  {outcome_text}')
        self.lbl_status.config(text='')

        self.lbl_bankroll.config(text=f'BANKROLL: ${self.bankroll}')
        self.btn_deal.config(state='normal')


if __name__ == '__main__':
    root = tk.Tk()
    app = BlackjackGUI(root)
    root.mainloop()