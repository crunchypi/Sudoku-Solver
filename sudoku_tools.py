

class Sudoku():
    """ This is a class for loading and solving a Sudoku puzzle

    Main features which are non-protected: 
        Loading a gameboard from CSV
        Solving gameboard with backtracking.
    
    Other methods are mainly for support and use of
    the two main features.
    """
    verbosity = False

    __board = None
    __sudoku_N = None
    
    __subgrid_row_count = None
    __subgrid_column_count = None
    __subgrid_coordinates = None

    __protected_coordinates = ()

    def __init__(self, verbosity: bool = False):
        self.verbosity = verbosity
    

    def get_board(self):
        return self.__board


    def get_sudoku_N(self):
        return self.__sudoku_N


    def get_subgrid_row_count(self):
        return self.__subgrid_row_count


    def get_subgrid_column_count(self):
        return self.__subgrid_column_count


    def get_protected_coordinates(self):
        return self.__protected_coordinates


    def condition_print(self, msg):
        if self.verbosity: print(msg)


    def load_board_csv(self, path : str, 
                        subgrid_row_count: int, 
                        subgrid_column_count: int):
        """ Loads valid Sudoku boards from CSV files.
            Requires: 
                - Path to CSV file.
                - Subgrid row count.
                - Subgrid column count.
                (subgrid row * subgrid column has equal one Sudoku side,
                 as is required for a valid Sudoku gameboard).

            Sets all required components of this class:
                - board.
                - sudoku_N (where N is the length of a Sudoku board side).
                - subgrid_row_count and subgrid_column_count.
                - subgrid_coordinates.
                - protected_coordinates (pre-filled numbers in the Sudoku board).

            Failure if:
                - File not found.
                - board is not a perfect square.
                - Non-integer values in loaded board.
                - Illegal subgrid configuration.
        """
        board = []
        try:
            with open(path, "r") as csv_file:
                board = [ row.strip("\n").split(",") for row in csv_file]
        except FileNotFoundError:
            self.condition_print(f"The file at path '{path}' was not found. Aborting.")
            return False

        for row in board:
            if len(row) != len(board):
                self.condition_print(f"Illegal configuration of csv file at '{path}'")
                return False


        # // Validation that row and column of subgrids is possible.
        if subgrid_row_count * subgrid_column_count != len(board):
            self.condition_print("Invalid configuration, aborting")
            return
            
        if not self.__convert_grid_str_to_int(board):
            return False

        if not self.__set_protected_coordinates(board):
            return False

        self.__board: list = board
        self.__sudoku_N: int = len(board)
        self.__subgrid_row_count: int = subgrid_row_count
        self.__subgrid_column_count: int = subgrid_column_count
        self.__set_subgrid_coordinates(subgrid_row_count,
                                        subgrid_column_count)
        return True

    def __convert_grid_str_to_int(self, board: list):
        """ Takes a grid of numeric strings and converts to integers.
            Note: Change in-place.

            Failure (False return) if a cell is not numeric.
        """
        for row_index in range(len(board)):
            for col_index in range(len(board)):
                try:
                    num = int(board[row_index][col_index])
                    board[row_index][col_index] = num
                except ValueError:
                    self.condition_print("Board cells can only consist" 
                                        "of numbers but found:" 
                                        f"'{board[row_index][col_index]}'"
                                        ". Aborting board setup.")
                    return False
        return True

    def __set_protected_coordinates(self, board: list):
        """ Caches coordinates of pre-filled numbers in a Sudoku gameboard.
        """
        protected_coordinates = []
        for row_index in range(len(board)):
            for col_index in range(len(board)):
                if board[row_index][col_index] != 0:
                    protected_coordinates.append([row_index,col_index])

        self.__protected_coordinates = tuple(protected_coordinates)
        return True


    def __set_subgrid_coordinates(self,
                                subgrid_row_count: int, 
                                subgrid_column_count: int):
        """ Sets coordinates of all subgrids specified for the gameboard.

            Requires: 
                    - Path to CSV file.
                    - Subgrid row count.
                    - Subgrid column count.
        """
        subgrids = []

        # // Create coordinates relative to subgrid.
        sub_coords = []
        for i in range(subgrid_row_count):
            for j in range(subgrid_column_count):
                sub_coords.append([i, j])

        # // Expand subgrid coordinates to cover the game-board.
        temp = []
        for i in range(subgrid_column_count):
            for j in range(subgrid_row_count):
                for sub in sub_coords:
                    new_x: int = i * subgrid_row_count + sub[0]
                    new_y: int = j * subgrid_column_count + sub[1]
                    temp.append([ new_x, new_y ]) 
                subgrids.append(temp.copy())
                temp.clear()

        self.__subgrid_coordinates: list = subgrids

    def __get_subgrid_from_coord(self, coordinate: list):
        """ Returns a relevant subgrid from a global coordinate.
            Requires:
                - Global (game-board) coordinate.
        """
        for sub in self.__subgrid_coordinates:
            for coord_pair in sub:
                if coord_pair == coordinate: 
                    return sub


    def __get_coord_from_index(self, index: int):
        """ Return a global gameboard coordinate from an index,
            where last index equals columns * rows - 1.

            Requres:
                - Index.
        """
        coord_row = index // self.__sudoku_N
        coord_col = index % self.__sudoku_N
        return [coord_row, coord_col]
    
    # // Check if a number is possible at game-board coordinate (Sudoku rules)
    def __validate_num_at_coord(self, num: int, coord: list):
        """ Check if a number is valid, based on a global (game-board) coordinate.
            This conforms to the Sudoku rule where a number cannot appear twice
            in a column, row or subgrid.

            Requires:
                - The number to check.
                - Global (game-board) coordinate.

            Returns:
                - Boolean.
        """
        # // Check rows & columns.
        for i in range(self.__sudoku_N):
            if num == self.__board[coord[0]][i]: return False # // Rows
            if num == self.__board[i][coord[1]]: return False # // Columns

        # // Check subgrid.
        subgrid_coords = self.__get_subgrid_from_coord(coord)
        subgrid_nums = [self.__board[c[0]][c[1]] for c in subgrid_coords]
        if num in subgrid_nums: return False

        return True
    

    def backtrack(self):
        """ Wrapper for the Sudoku solver.
            Starts the Sudoku solver if all required properties are set

            Returns 'True' if a solution is Found.
        """
        # // Ensures that a gameboard is existing before recursion.
        if self.__board is None: return False
        if self.__sudoku_N is None: return False
        if self.__subgrid_coordinates is None: return False

        # // Nesting allows the ensurance block to be executed before recursion.
        def process_board(current_index : int = 0):
            """ Solves a Sudoku game, as long as a solution is possible.
                Is an implementation of a generalised backtracking algorithm,
                with the use of recursion.

                Returns a Boolean depending on whether or not a solution is found. 
            """
            if current_index >= self.__sudoku_N ** 2 : # // sudoku_N ** 2 is end.
                return True

            coord: list = self.__get_coord_from_index(current_index)
            for d in range(1, self.__sudoku_N + 1):
                if self.__validate_num_at_coord(d, coord):
                    self.__board[coord[0]][coord[1]] = d

                    next_index: int = current_index + 1
                    next_coord: list = self.__get_coord_from_index(current_index + 1)
                    if next_coord in self.__protected_coordinates: # // Skip a step if next is protected.
                        next_index += 1
                    
                    if process_board(next_index):
                        return True

            self.__board[coord[0]][coord[1]] = 0 # // Reset cell if branch failed.
            return False

        if process_board():
            self.condition_print("Board has at least one solution.")
            return True
        else:
            self.condition_print("Board has no solutions.")
            return False
            