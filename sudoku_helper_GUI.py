import tkinter as tk
from tkinter.ttk import Separator, Style
import sudoku_tools

class GUIInterface():
    """ A GUI interface for a Sudoku solver. 

        Requires:
            - Tkinter.
            - Sudoku loader and solver.

        Has two main views/frames:
            - Top for loading a Sudoku board.
            - Bottom for displaying a Sudoku grid.
    """
    __sudoku = None

    __window = None
    __frame_top = None
    __frame_grid = None

    __path_entry = None
    __subgrid_row_entry = None
    __subgrid_column_entry = None

    __grid_var = None
    __grid_box = None


    def __init__(self):
        """ Setup for a Sudoku module and TKinter grids.
            Initiates a Tkinter main loop.
        """
        self.__sudoku = sudoku_tools.Sudoku()

        self.__window = tk.Tk()
        self.__window.title("Sudoku Solver")

        self.__frame_top = tk.Frame(self.__window, borderwidth=0, relief="solid")
        self.__frame_top.pack()
        self.__frame_grid = tk.Frame(self.__window, borderwidth=0, relief="solid")
        self.__frame_grid.pack()
        
        self.__setup_top_interface()

        self.__window.mainloop()
        

    def __setup_top_interface(self):
        """ Fills the top frame with labels, input fiels 
            and buttons necessary for loading a Sudoku board.
        """
        const_width = 20
        const_text_size = 10

        # // For path.
        path_label = tk.Label(self.__frame_top, text="Path to CSV")
        path_label.config(font=("Courier", const_text_size))
        path_label.config(width=const_width)
        path_label.grid(row=0, column=0)
        path_entry = tk.Entry(self.__frame_top, width=const_width)
        path_entry.grid(row=1,column=0)
        self.__path_entry = path_entry

        # // For subgrid row specification.
        subgrid_row_label = tk.Label(self.__frame_top, text="Subgrid row count")
        subgrid_row_label.config(font=("Courier", const_text_size))
        subgrid_row_label.config(width=const_width)
        subgrid_row_label.grid(row=0, column=1)
        subgrid_row_entry = tk.Entry(self.__frame_top, width=const_width)
        subgrid_row_entry.grid(row=1,column=1)
        self.__subgrid_row_entry = subgrid_row_entry

        # // For subgrid column specification.
        subgrid_column_label = tk.Label(self.__frame_top, text="Subgrid column count")
        subgrid_column_label.config(font=("Courier", const_text_size))
        subgrid_column_label.config(width=const_width)
        subgrid_column_label.grid(row=0, column=2)
        subgrid_column_entry = tk.Entry(self.__frame_top, width=const_width)
        subgrid_column_entry.grid(row=1,column=2)
        self.__subgrid_column_entry = subgrid_column_entry

        # // Submit button.
        path_btn = tk.Button(self.__frame_top, text="Load")
        path_btn.config(highlightbackground="#000000")
        path_btn.config(font=("Courier", const_text_size))
        path_btn.config(width=int(const_width/3))
        path_btn.config(command=self.__load_board)
        path_btn.grid(row=1, column=5)
        path_btn.update()


    def __load_board(self):
        """ Uses input data from top fram to load a Sudoku game.
            Sudoku game solver is called from here (GUI grid
            creation is called on success).
        """
        # // Value access.
        path: str = self.__path_entry.get()
        subgrid_rows: str = self.__subgrid_row_entry.get()
        subgrid_cols: str = self.__subgrid_column_entry.get()
        safe_pass = True

        # // Error logic.
        if subgrid_rows.isdigit():
            subgrid_rows = int(subgrid_rows)
        else:
            self.__subgrid_row_entry.delete(0, tk.END)
            self.__subgrid_row_entry.insert(0,"Invalid")
            safe_pass = False

        if subgrid_cols.isdigit():
            subgrid_cols = int(subgrid_cols)
        else:
            self.__subgrid_column_entry.delete(0, tk.END)
            self.__subgrid_column_entry.insert(0,"Invalid") 
            safe_pass = False

        # // Board creation.
        if safe_pass:
            loaded: bool = self.__sudoku.load_board_csv(path, subgrid_rows, subgrid_cols)
            if loaded: 
                solved: bool = self.__sudoku.backtrack()
                if solved:
                    self.__frame_grid.destroy()
                    self.__frame_grid = tk.Frame(self.__window, borderwidth=0, relief="solid")
                    self.__frame_grid.pack()
                    self.__setup_grid()
                    self.__setup_separators()
                else:
                    self.__path_entry.delete(0, tk.END)
                    self.__path_entry.insert(0,"Unsolvable")
            else:
                self.__path_entry.delete(0, tk.END)
                self.__path_entry.insert(0,"Loading failure")


    def __on_cell_input(self, cell_id: str, unused_1: str, unused_2: str):
        """ Callback for tracked cells in the GUI grid.
            Compares GUI cell values against pre-solved Sudoku grid values
            and does appropriate colorisation of GUI cells.
        """
        # // Value access.
        coord: list = self.__get_coord_from_var(cell_id)
        box: tkinter.Entry = self.__grid_box[coord[0]][coord[1]]
        game_board: list = self.__sudoku.get_board()
        game_board_result: int = game_board[coord[0]][coord[1]]
        user_input: str = self.__grid_var[coord[0]][coord[1]].get()

        # // Colorisation logic.
        bg = "red"
        if user_input == "":
            bg = "white"
        if user_input.isdigit():
            user_input = int(user_input)
            if user_input == game_board_result:
                bg = "green"
        box.config(bg=bg)


    def __get_coord_from_var(self, cell_id: str):
        """ Finds the coordinate (in a matrix) where 
            a Tkinter cell is cached, based on tags.
        """
        for i in range(len(self.__grid_var)):
            for j in range(len(self.__grid_var)): 
                if str(self.__grid_var[i][j]) == str(cell_id): # // Compare tags.
                    return [i,j]


    def __setup_grid(self):
        """ Duplicates a Sudoku game-board onto a GUI grid.
            Cells consist of Tkinter values (StringVar) and entries (Entry).
            Cells are stored in a matrix for later retrieval (to check
            if a user enters a correct value, according to a pre-solved
            Sudoku board).
        """
        board: list = self.__sudoku.get_board()

        grid_var = []
        grid_box = []
        temp_var = []
        temp_box = []

        for i in range(len(board)):
            for j in range(len(board)):

                new_var = tk.StringVar()
                new_box = tk.Entry(self.__frame_grid, textvariable=new_var, width=4)
                new_box.grid(row=i,column=j)

                if [i,j] in self.__sudoku.get_protected_coordinates():
                    new_var.set(board[i][j])
                    new_box.config(bg="gray")
                    new_box.config(state="disabled")
                else:
                    new_var.set("")
                
                new_var.trace("w", self.__on_cell_input)
                temp_var.append(new_var)
                temp_box.append(new_box)

            grid_var.append(temp_var.copy())
            grid_box.append(temp_box.copy())
            temp_var.clear()
            temp_box.clear()

        self.__grid_var: list = grid_var
        self.__grid_box: list = grid_box


    def __setup_separators(self):
        """ Draws separator lines to visualise subgrids 
        """
        self.__frame_grid.update()

        # // Value access.
        height: int = self.__frame_grid.winfo_height()
        width: int = self.__frame_grid.winfo_width()
        row_count: int = self.__frame_grid.size()[0]

        # // Draw subgrid.
        for x in range(row_count):
            if x % self.__sudoku.get_subgrid_row_count() == 0:
                line = tk.ttk.Separator(self.__frame_grid, orient=tk.HORIZONTAL)
                line.place(width=width, height=1, x=0, y=height / row_count * x )

            if x % self.__sudoku.get_subgrid_column_count( )== 0:
                line = line = tk.ttk.Separator(self.__frame_grid, orient=tk.VERTICAL)
                line.place(width=1, height=height, x=width / row_count * x , y=0 )

        # // Finishing edges.
        line = tk.ttk.Separator(self.__frame_grid, orient=tk.HORIZONTAL)
        line.place(width=width, height=1, x=0, y=height - 1 )
        line = line = tk.ttk.Separator(self.__frame_grid, orient=tk.VERTICAL)
        line.place(width=1, height=height, x=width - 1 , y=0 )


start = GUIInterface()