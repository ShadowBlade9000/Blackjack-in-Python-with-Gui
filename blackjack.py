import random
import tkinter as tk
from tkinter import messagebox

# Card definitions
SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
          'J': 10, 'Q': 10, 'K': 10, 'A': 11}
SUIT_SYMBOLS = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}
SUIT_COLORS = {'Hearts': 'red', 'Diamonds': 'red', 'Clubs': 'black', 'Spades': 'black'}


def create_deck():
    """Create and shuffle a standard 52-card deck."""
    deck = [{'rank': rank, 'suit': suit} for suit in SUITS for rank in RANKS]
    random.shuffle(deck)
    return deck


def calculate_score(hand):
    """Calculate the best score for a hand, treating Aces as 1 or 11."""
    score = sum(VALUES[card['rank']] for card in hand)
    aces = sum(1 for card in hand if card['rank'] == 'A')
    while score > 21 and aces > 0:
        score -= 10
        aces -= 1
    return score


class BlackjackGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Blackjack")
        self.root.geometry("700x550")
        self.root.configure(bg="#1c5e31")  # Felt green background

        self.deck = []
        self.player_hand = []
        self.dealer_hand = []
        self.game_over = False

        self._build_ui()
        self.start_new_game()

    def _build_ui(self):
        # Title Header
        title_label = tk.Label(
            self.root, text="BLACKJACK", font=("Helvetica", 24, "bold"),
            bg="#1c5e31", fg="#ffd700"
        )
        title_label.pack(pady=10)

        # Status Label (Game outcome message)
        self.status_label = tk.Label(
            self.root, text="", font=("Helvetica", 14, "bold"),
            bg="#1c5e31", fg="#ffffff"
        )
        self.status_label.pack(pady=5)

        # Dealer Section
        self.dealer_frame = tk.LabelFrame(
            self.root, text=" Dealer's Hand ", font=("Helvetica", 12, "bold"),
            bg="#1c5e31", fg="#ffffff", bd=2, relief="groove"
        )
        self.dealer_frame.pack(padx=20, pady=10, fill="x")

        self.dealer_score_label = tk.Label(
            self.dealer_frame, text="Score: ?", font=("Helvetica", 11),
            bg="#1c5e31", fg="#ffffff"
        )
        self.dealer_score_label.pack(anchor="w", padx=10, pady=2)

        self.dealer_cards_frame = tk.Frame(self.dealer_frame, bg="#1c5e31")
        self.dealer_cards_frame.pack(padx=10, pady=10)

        # Player Section
        self.player_frame = tk.LabelFrame(
            self.root, text=" Your Hand ", font=("Helvetica", 12, "bold"),
            bg="#1c5e31", fg="#ffffff", bd=2, relief="groove"
        )
        self.player_frame.pack(padx=20, pady=10, fill="x")

        self.player_score_label = tk.Label(
            self.player_frame, text="Score: 0", font=("Helvetica", 11),
            bg="#1c5e31", fg="#ffffff"
        )
        self.player_score_label.pack(anchor="w", padx=10, pady=2)

        self.player_cards_frame = tk.Frame(self.player_frame, bg="#1c5e31")
        self.player_cards_frame.pack(padx=10, pady=10)

        # Controls Section
        control_frame = tk.Frame(self.root, bg="#1c5e31")
        control_frame.pack(pady=15)

        self.hit_btn = tk.Button(
            control_frame, text="Hit", font=("Helvetica", 12, "bold"),
            width=10, bg="#2e8b57", fg="white", activebackground="#3cb371",
            command=self.hit
        )
        self.hit_btn.grid(row=0, column=0, padx=10)

        self.stand_btn = tk.Button(
            control_frame, text="Stand", font=("Helvetica", 12, "bold"),
            width=10, bg="#b22222", fg="white", activebackground="#cd5c5c",
            command=self.stand
        )
        self.stand_btn.grid(row=0, column=1, padx=10)

        self.new_game_btn = tk.Button(
            control_frame, text="New Game", font=("Helvetica", 12, "bold"),
            width=10, bg="#1e90ff", fg="white", activebackground="#63b8ff",
            command=self.start_new_game
        )
        self.new_game_btn.grid(row=0, column=2, padx=10)

    def draw_card_widget(self, parent, card, face_down=False):
        """Draws a visual card item inside a Tkinter Canvas."""
        canvas = tk.Canvas(parent, width=70, height=100, bg="#1c5e31", highlightthickness=0)
        
        if face_down:
            # Draw card back
            canvas.create_rectangle(2, 2, 68, 98, fill="#b22222", outline="#ffffff", width=2)
            canvas.create_rectangle(8, 8, 62, 92, fill="#8b0000", outline="#ffffff", width=1)
        else:
            # Draw card face
            canvas.create_rectangle(2, 2, 68, 98, fill="#ffffff", outline="#333333", width=2)
            color = SUIT_COLORS[card['suit']]
            symbol = SUIT_SYMBOLS[card['suit']]
            
            # Rank top-left and bottom-right
            canvas.create_text(12, 14, text=card['rank'], font=("Helvetica", 10, "bold"), fill=color)
            canvas.create_text(58, 86, text=card['rank'], font=("Helvetica", 10, "bold"), fill=color)
            
            # Suit symbol in center
            canvas.create_text(35, 50, text=symbol, font=("Helvetica", 22), fill=color)

        canvas.pack(side="left", padx=5)

    def update_display(self, show_dealer_hidden=True):
        """Redraw dealer and player card frames."""
        for widget in self.dealer_cards_frame.winfo_children():
            widget.destroy()
        for widget in self.player_cards_frame.winfo_children():
            widget.destroy()

        # Render dealer hand
        if show_dealer_hidden and len(self.dealer_hand) >= 2:
            self.draw_card_widget(self.dealer_cards_frame, self.dealer_hand[0])
            self.draw_card_widget(self.dealer_cards_frame, None, face_down=True)
            self.dealer_score_label.config(
                text=f"Score: {VALUES[self.dealer_hand[0]['rank']]} + ?"
            )
        else:
            for card in self.dealer_hand:
                self.draw_card_widget(self.dealer_cards_frame, card)
            self.dealer_score_label.config(text=f"Score: {calculate_score(self.dealer_hand)}")

        # Render player hand
        for card in self.player_hand:
            self.draw_card_widget(self.player_cards_frame, card)
        player_score = calculate_score(self.player_hand)
        self.player_score_label.config(text=f"Score: {player_score}")

    def start_new_game(self):
        self.deck = create_deck()
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]
        self.game_over = False

        self.status_label.config(text="Your turn! Hit or Stand?")
        self.hit_btn.config(state="normal")
        self.stand_btn.config(state="normal")

        self.update_display(show_dealer_hidden=True)

        # Check for immediate natural Blackjack
        if calculate_score(self.player_hand) == 21:
            self.stand()

    def hit(self):
        if self.game_over:
            return

        self.player_hand.append(self.deck.pop())
        player_score = calculate_score(self.player_hand)

        if player_score > 21:
            self.update_display(show_dealer_hidden=False)
            self.end_game("Bust! You exceeded 21. Dealer Wins!")
        else:
            self.update_display(show_dealer_hidden=True)

    def stand(self):
        if self.game_over:
            return

        # Dealer turn: draw until score is at least 17
        dealer_score = calculate_score(self.dealer_hand)
        while dealer_score < 17:
            self.dealer_hand.append(self.deck.pop())
            dealer_score = calculate_score(self.dealer_hand)

        player_score = calculate_score(self.player_hand)
        self.update_display(show_dealer_hidden=False)

        # Determine winner
        if dealer_score > 21:
            self.end_game("Dealer busted! You Win!")
        elif player_score > dealer_score:
            self.end_game("You Win!")
        elif player_score < dealer_score:
            self.end_game("Dealer Wins!")
        else:
            self.end_game("It's a Tie (Push)!")

    def end_game(self, message):
        self.game_over = True
        self.status_label.config(text=message)
        self.hit_btn.config(state="disabled")
        self.stand_btn.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = BlackjackGUI(root)
    root.mainloop()