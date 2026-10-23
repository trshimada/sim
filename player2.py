from __future__ import annotations
from consts import Board, Color, Edge, NUM_NODES
from itertools import combinations

class Player2:
    """
    Implements a winning strategy for the second player in a game of Sim
    """

    @staticmethod
    def get_move(board: Board) -> Edge:
        """
        Return a possible move for the second player (blue) that follows the optimal strategy laid out in the handout,
        given the input board state. If multiple moves are viable, this method can return any of them.
        """
        # Select a miniboard for the current board
        miniboard = Player2.get_miniboard(board)
        if miniboard is None:
            allowed = Player2.get_allowed_moves(Color.P2, board)
            return allowed[0] if allowed else (0, 1)

        # Look at the set of moves P2 can make in the miniboard. If there is only one move, select this move.
        p2_moves = Player2.get_allowed_moves(Color.P2, miniboard)
        if len(p2_moves) == 1:
            return p2_moves[0]

        # Consider the moves in the largest number of sets in moves P2 can make
        max_p2_sets = Player2.get_maximal_allowed_sets(Color.P2, miniboard)

        move_counts_p2 = {}
        for move in p2_moves:
            count = 0
            for s in max_p2_sets:
                # Check if the move is in the maximum set
                if move in s or (move[1], move[0]) in s:
                    count += 1
            move_counts_p2[move] = count

        # Find the highest frequency count among P2 moves
        max_count_p2 = -1
        for count in move_counts_p2.values():
            if count > max_count_p2:
                max_count_p2 = count

        # Collect all moves that share this count
        best_moves_p2 = []
        for move, count in move_counts_p2.items():
            if count == max_count_p2:
                best_moves_p2.append(move)

        if len(best_moves_p2) == 1:
            return best_moves_p2[0]

        # Consider the moves in the largest number of sets in moves P1 can make
        max_p1_sets = Player2.get_maximal_allowed_sets(Color.P1, miniboard)

        move_counts_p1 = {}
        for move in best_moves_p2:
            count = 0
            for s in max_p1_sets:
                if move in s or (move[1], move[0]) in s:
                    count += 1
            move_counts_p1[move] = count

        # Find the highest frequency count among P1 sets
        max_count_p1 = -1
        for count in move_counts_p1.values():
            if count > max_count_p1:
                max_count_p1 = count

        # Gather best moves and pick one
        best_moves_p1 = []
        for move, count in move_counts_p1.items():
            if count == max_count_p1:
                best_moves_p1.append(move)

        return best_moves_p1[0] if best_moves_p1 else best_moves_p2[0]

    @staticmethod
    def get_miniboard(board: Board) -> Board | None:
        """
        Return a miniboard from the input board state. If there are multiple miniboards, this method can return any of them.
        """
        # Find all nodes with at least one colored edge on the current board
        colored_nodes = set()
        for i in range(NUM_NODES):
            for j in range(NUM_NODES):
                if board[i][j] in (Color.P1, Color.P2):
                    colored_nodes.add(i)
                    colored_nodes.add(j)

        all_nodes = list(range(NUM_NODES))
        valid_miniboards = []

        # Iterate over all possible subsets of nodes
        for r in range(1, NUM_NODES + 1):
            for node_subset in combinations(all_nodes, r):
                node_set = set(node_subset)

                # Must contain at least every colored node
                if not colored_nodes.issubset(node_set):
                    continue

                # Each node must be connected to each other node
                complete = True
                for i in node_set:
                    for j in node_set:
                        if i != j and board[i][j] == Color.NONE:
                            complete = False
                            break
                    if not complete:
                        break
                if not complete:
                    continue

                # Build a mini-board for this subset of nodes
                mini_board = [[Color.NONE] * NUM_NODES for _ in range(NUM_NODES)]
                for i in node_set:
                    for j in node_set:
                        mini_board[i][j] = board[i][j]

                # Must contain at least one move P2 can make
                p2_allowed = Player2.get_allowed_moves(Color.P2, mini_board)
                if len(p2_allowed) == 0:
                    continue

                valid_miniboards.append((node_set, mini_board))

        if not valid_miniboards:
            return None

        # Cannot remove a subset while still satisfying conditions
        for node_set, mini_board in valid_miniboards:
            is_minimal = True
            for other_node_set, other_mini_board in valid_miniboards:
                if other_node_set.issubset(node_set) and other_node_set != node_set:
                    is_minimal = False
                    break
            if is_minimal:
                return mini_board

        return valid_miniboards[0][1]

    @staticmethod
    def get_maximal_allowed_sets(player: Color, board: Board) -> set[frozenset[Edge]]:
        """
        Return a set of all distinct maximal allowed sets for the given player over the input board state.
        If player is Color.P1, find all maximal p1-allowed sets; if player is Color.P2, find all maximal p2-allowed sets.
        """
        allowed_moves = Player2.get_allowed_moves(player, board)
        valid_sets = []
        max_size = -1

        # Check all possible combinations of allowed moves to find valid sets
        for r in range(len(allowed_moves) + 1):
            for combo in combinations(allowed_moves, r):

                # Create a temporary board so we can test adding this combination of moves
                temp_board = [row[:] for row in board]
                for u, v in combo:
                    temp_board[u] = temp_board[u][:]
                    temp_board[u][v] = player
                    temp_board[v] = temp_board[v][:]
                    temp_board[v][u] = player

                # Test if any single colored triangle is formed by this combination
                has_triangle = False
                for i in range(NUM_NODES):
                    for j in range(i + 1, NUM_NODES):
                        for k in range(j + 1, NUM_NODES):
                            if (temp_board[i][j] == player and
                                    temp_board[j][k] == player and
                                    temp_board[k][i] == player):
                                has_triangle = True
                                break
                        if has_triangle:
                            break
                    if has_triangle:
                        break

                # If no triangle was formed, this is a valid allowed set
                if not has_triangle:
                    fs = frozenset(combo)
                    size = len(fs)

                    # We want to keep track of the maximal sets
                    if size > max_size:
                        max_size = size
                        valid_sets = [fs]
                    elif size == max_size:
                        if fs not in valid_sets:
                            valid_sets.append(fs)

        return set(valid_sets)

    @staticmethod
    def get_allowed_moves(player: Color, board: Board) -> list[Edge]:
        """
        Return a list of all distinct valid moves for the given player over the input board state.
        """
        allowed_moves = []

        for i in range(NUM_NODES):
            for j in range(i + 1, NUM_NODES):
                # An edge must exist and be uncolored
                if board[i][j] == Color.UNCOLORED:
                    forms_triangle = False

                    # Check if coloring this edge would form a triangle
                    for k in range(NUM_NODES):
                        if k != i and k != j:
                            if board[i][k] == player and board[j][k] == player:
                                forms_triangle = True
                                break

                    # If it doesn't form a triangle, it's a valid move
                    if not forms_triangle:
                        allowed_moves.append((i, j))

        return allowed_moves
