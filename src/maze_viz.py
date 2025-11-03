import matplotlib.pyplot as plt
from matplotlib import animation
import logging

logging.basicConfig(level=logging.DEBUG)


class Visualizer(object):
    """Class that handles all aspects of visualization.


    Attributes:
        maze: The maze that will be visualized
        cell_size (int): How large the cells will be in the plots
        height (int): The height of the maze
        width (int): The width of the maze
        ax: The axes for the plot
        lines:
        squares:
        media_filename (string): The name of the animations and images

    """
    def __init__(self, maze, cell_size, media_filename, show_text=True):
        self.maze = maze
        self.cell_size = cell_size
        self.height = maze.num_rows * cell_size
        self.width = maze.num_cols * cell_size
        self.ax = None
        self.lines = dict()
        self.squares = dict()
        self.media_filename = media_filename
        self.show_text = show_text
        self.wall_linewidth = 40
        self.outline_linewidth = 40

    def set_media_filename(self, filename):
        """Sets the filename of the media
            Args:
                filename (string): The name of the media
        """
        self.media_filename = filename

    def show_maze(self, display=True):
        """Displays a plot of the maze without the solution path"""

        # Create the plot figure and style the axes
        fig = self.configure_plot()

        # Plot the walls on the figure
        self.plot_walls()

        # Handle any potential saving
        if self.media_filename:
            fig.savefig("{}{}.png".format(self.media_filename, "_generation"), bbox_inches='tight', pad_inches=0)

        # Display the plot to the user
        if display:
            plt.show()
        else:
            plt.close(fig)

    def plot_walls(self):
        """ Plots the walls of a maze. This is used when generating the maze image"""
        pad_x, pad_y = self._points_to_data_units(self.outline_linewidth / 2.0)

        if pad_x > 0 or pad_y > 0:
            frame = plt.Rectangle((-pad_x, -pad_y), self.width + 2 * pad_x, self.height + 2 * pad_y,
                                  facecolor='black', edgecolor='none', zorder=0)
            frame.set_clip_on(False)
            self.ax.add_patch(frame)

        background = plt.Rectangle((0, 0), self.width, self.height,
                                    facecolor='white', edgecolor='none', zorder=1)
        self.ax.add_patch(background)

        for i in range(self.maze.num_rows):
            for j in range(self.maze.num_cols):
                # Add colored squares for entry and exit
                cell = self.maze.initial_grid[i][j]
                if cell.is_entry_exit == "entry":
                    # Green square for start (smaller, centered; apply compensation if outline intrudes)
                    small_size = self.cell_size // 3
                    base_offset = (self.cell_size - small_size) / 2
                    compensation_x, compensation_y = self._get_border_compensation()

                    x_offset = base_offset
                    y_offset = base_offset

                    # Adjust offset based on which edge has the opening (border)
                    if not cell.walls["top"]:
                        y_offset += compensation_y  # Push down from top border
                    elif not cell.walls["bottom"]:
                        y_offset -= compensation_y  # Push up from bottom border
                    elif not cell.walls["left"]:
                        x_offset += compensation_x  # Push right from left border
                    elif not cell.walls["right"]:
                        x_offset -= compensation_x  # Push left from right border

                    entry_square = plt.Rectangle((j*self.cell_size + x_offset, i*self.cell_size + y_offset),
                                                  small_size, small_size,
                                                  facecolor='green', edgecolor='none')
                    self.ax.add_patch(entry_square)
                elif cell.is_entry_exit == "exit":
                    # Red square for exit (smaller, centered; apply compensation if outline intrudes)
                    small_size = self.cell_size // 3
                    base_offset = (self.cell_size - small_size) / 2
                    compensation_x, compensation_y = self._get_border_compensation()

                    x_offset = base_offset
                    y_offset = base_offset

                    # Adjust offset based on which edge has the opening (border)
                    if not cell.walls["top"]:
                        y_offset += compensation_y  # Push down from top border
                    elif not cell.walls["bottom"]:
                        y_offset -= compensation_y  # Push up from bottom border
                    elif not cell.walls["left"]:
                        x_offset += compensation_x  # Push right from left border
                    elif not cell.walls["right"]:
                        x_offset -= compensation_x  # Push left from right border

                    exit_square = plt.Rectangle((j*self.cell_size + x_offset, i*self.cell_size + y_offset),
                                                 small_size, small_size,
                                                 facecolor='red', edgecolor='none')
                    self.ax.add_patch(exit_square)

                if self.show_text:
                    if self.maze.initial_grid[i][j].is_entry_exit == "entry":
                        self.ax.text(j*self.cell_size, i*self.cell_size, "START", fontsize=7, weight="bold")
                    elif self.maze.initial_grid[i][j].is_entry_exit == "exit":
                        self.ax.text(j*self.cell_size, i*self.cell_size, "END", fontsize=7, weight="bold")

                if self._should_draw_wall(cell, i, j, "top"):
                    self.ax.plot([j*self.cell_size, (j+1)*self.cell_size],
                                 [i*self.cell_size, i*self.cell_size], color="k", linewidth=self.wall_linewidth)
                if self._should_draw_wall(cell, i, j, "right"):
                    self.ax.plot([(j+1)*self.cell_size, (j+1)*self.cell_size],
                                 [i*self.cell_size, (i+1)*self.cell_size], color="k", linewidth=self.wall_linewidth)
                if self._should_draw_wall(cell, i, j, "bottom"):
                    self.ax.plot([(j+1)*self.cell_size, j*self.cell_size],
                                 [(i+1)*self.cell_size, (i+1)*self.cell_size], color="k", linewidth=self.wall_linewidth)
                if self._should_draw_wall(cell, i, j, "left"):
                    self.ax.plot([j*self.cell_size, j*self.cell_size],
                                 [(i+1)*self.cell_size, i*self.cell_size], color="k", linewidth=self.wall_linewidth)

    def configure_plot(self):
        """Sets the initial properties of the maze plot. Also creates the plot and axes"""

        # Create the plot figure
        fig = plt.figure(figsize = (7, 7*self.maze.num_rows/self.maze.num_cols))

        # Create the axes
        self.ax = plt.axes()

        # Set an equal aspect ratio
        self.ax.set_aspect("equal")

        # Remove the axes from the figure
        self.ax.axes.get_xaxis().set_visible(False)
        self.ax.axes.get_yaxis().set_visible(False)

        # Remove spines (borders)
        for spine in self.ax.spines.values():
            spine.set_visible(False)

        # Set axis limits to exactly fit the maze
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)

        if self.show_text:
            title_box = self.ax.text(0, self.maze.num_rows + self.cell_size + 0.1,
                                r"{}$\times${}".format(self.maze.num_rows, self.maze.num_cols),
                                bbox={"facecolor": "gray", "alpha": 0.5, "pad": 4}, fontname="serif", fontsize=15)

        return fig

    def _points_to_data_units(self, points):
        """Convert a length specified in points to data units for the current axes."""

        if self.ax is None:
            return 0.0, 0.0

        fig = self.ax.figure
        pixels = points * (fig.dpi / 72.0)

        origin_disp = self.ax.transData.transform((0, 0))
        unit_x_disp = self.ax.transData.transform((1, 0))
        unit_y_disp = self.ax.transData.transform((0, 1))

        pixels_per_data_x = unit_x_disp[0] - origin_disp[0]
        pixels_per_data_y = unit_y_disp[1] - origin_disp[1]

        pad_x = pixels / pixels_per_data_x if pixels_per_data_x != 0 else 0.0
        pad_y = pixels / pixels_per_data_y if pixels_per_data_y != 0 else 0.0

        return pad_x, pad_y

    def _get_border_compensation(self):
        """Return the data-unit offset required to compensate for outline overhang."""

        points_difference = max(0.0, self.outline_linewidth - self.wall_linewidth) / 2.0
        return self._points_to_data_units(points_difference)

    def _should_draw_wall(self, cell, row_idx, col_idx, side):
        """Determine if a wall segment should be rendered for a given cell side."""

        if cell.walls[side]:
            return True

        if cell.is_entry_exit is None:
            return False

        if side == "top" and row_idx == 0:
            return True
        if side == "bottom" and row_idx == self.maze.num_rows - 1:
            return True
        if side == "left" and col_idx == 0:
            return True
        if side == "right" and col_idx == self.maze.num_cols - 1:
            return True

        return False

    def show_maze_solution(self):
        """Function that plots the solution to the maze. Also adds indication of entry and exit points."""

        # Create the figure and style the axes
        fig = self.configure_plot()

        # Plot the walls onto the figure
        self.plot_walls()

        list_of_backtrackers = [path_element[0] for path_element in self.maze.solution_path if path_element[1]]

        # Keeps track of how many circles have been drawn
        circle_num = 0

        self.ax.add_patch(plt.Circle(((self.maze.solution_path[0][0][1] + 0.5)*self.cell_size,
                                      (self.maze.solution_path[0][0][0] + 0.5)*self.cell_size), 0.2*self.cell_size,
                                     fc=(0, circle_num/(len(self.maze.solution_path) - 2*len(list_of_backtrackers)),
                                         0), alpha=0.4))

        for i in range(1, self.maze.solution_path.__len__()):
            if self.maze.solution_path[i][0] not in list_of_backtrackers and\
                    self.maze.solution_path[i-1][0] not in list_of_backtrackers:
                circle_num += 1
                self.ax.add_patch(plt.Circle(((self.maze.solution_path[i][0][1] + 0.5)*self.cell_size,
                    (self.maze.solution_path[i][0][0] + 0.5)*self.cell_size), 0.2*self.cell_size,
                    fc = (0, circle_num/(len(self.maze.solution_path) - 2*len(list_of_backtrackers)), 0), alpha = 0.4))

        # Display the plot to the user
        plt.show()

        # Handle any saving
        if self.media_filename:
            fig.savefig("{}{}.png".format(self.media_filename, "_solution"), bbox_inches='tight', pad_inches=0)

    def show_generation_animation(self):
        """Function that animates the process of generating the a maze where path is a list
        of coordinates indicating the path taken to carve out (break down walls) the maze."""

        # Create the figure and style the axes
        fig = self.configure_plot()

        # The square that represents the head of the algorithm
        indicator = plt.Rectangle((self.maze.generation_path[0][0]*self.cell_size, self.maze.generation_path[0][1]*self.cell_size),
            self.cell_size, self.cell_size, fc = "purple", alpha = 0.6)

        self.ax.add_patch(indicator)

        # Only need to plot right and bottom wall for each cell since walls overlap.
        # Also adding squares to animate the path taken to carve out the maze.
        color_walls = "k"
        for i in range(self.maze.num_rows):
            for j in range(self.maze.num_cols):
                self.lines["{},{}: right".format(i, j)] = self.ax.plot([(j+1)*self.cell_size, (j+1)*self.cell_size],
                        [i*self.cell_size, (i+1)*self.cell_size],
                    linewidth = 2, color = color_walls)[0]
                self.lines["{},{}: bottom".format(i, j)] = self.ax.plot([(j+1)*self.cell_size, j*self.cell_size],
                        [(i+1)*self.cell_size, (i+1)*self.cell_size],
                    linewidth = 2, color = color_walls)[0]

                self.squares["{},{}".format(i, j)] = plt.Rectangle((j*self.cell_size,
                    i*self.cell_size), self.cell_size, self.cell_size, fc = "red", alpha = 0.4)
                self.ax.add_patch(self.squares["{},{}".format(i, j)])

        # Plotting boundaries of maze.
        color_boundary = "k"
        self.ax.plot([0, self.width], [self.height,self.height], linewidth = 2, color = color_boundary)
        self.ax.plot([self.width, self.width], [self.height, 0], linewidth = 2, color = color_boundary)
        self.ax.plot([self.width, 0], [0, 0], linewidth = 2, color = color_boundary)
        self.ax.plot([0, 0], [0, self.height], linewidth = 2, color = color_boundary)

        def animate(frame):
            """Function to supervise animation of all objects."""
            animate_walls(frame)
            animate_squares(frame)
            animate_indicator(frame)
            self.ax.set_title("Step: {}".format(frame + 1), fontname="serif", fontsize=19)
            return []

        def animate_walls(frame):
            """Function that animates the visibility of the walls between cells."""
            if frame > 0:
                self.maze.grid[self.maze.generation_path[frame-1][0]][self.maze.generation_path[frame-1][1]].remove_walls(
                    self.maze.generation_path[frame][0],
                    self.maze.generation_path[frame][1])   # Wall between curr and neigh

                self.maze.grid[self.maze.generation_path[frame][0]][self.maze.generation_path[frame][1]].remove_walls(
                    self.maze.generation_path[frame-1][0],
                    self.maze.generation_path[frame-1][1])   # Wall between neigh and curr

                current_cell = self.maze.grid[self.maze.generation_path[frame-1][0]][self.maze.generation_path[frame-1][1]]
                next_cell = self.maze.grid[self.maze.generation_path[frame][0]][self.maze.generation_path[frame][1]]

                """Function to animate walls between cells as the search goes on."""
                for wall_key in ["right", "bottom"]:    # Only need to draw two of the four walls (overlap)
                    if current_cell.walls[wall_key] is False:
                        self.lines["{},{}: {}".format(current_cell.row,
                            current_cell.col, wall_key)].set_visible(False)
                    if next_cell.walls[wall_key] is False:
                        self.lines["{},{}: {}".format(next_cell.row,
                                                 next_cell.col, wall_key)].set_visible(False)

        def animate_squares(frame):
            """Function to animate the searched path of the algorithm."""
            self.squares["{},{}".format(self.maze.generation_path[frame][0],
                                   self.maze.generation_path[frame][1])].set_visible(False)
            return []

        def animate_indicator(frame):
            """Function to animate where the current search is happening."""
            indicator.set_xy((self.maze.generation_path[frame][1]*self.cell_size,
                              self.maze.generation_path[frame][0]*self.cell_size))
            return []

        logging.debug("Creating generation animation")
        anim = animation.FuncAnimation(fig, animate, frames=self.maze.generation_path.__len__(),
                                       interval=100, blit=True, repeat=False)

        logging.debug("Finished creating the generation animation")

        # Display the plot to the user
        plt.show()

        # Handle any saving
        if self.media_filename:
            print("Saving generation animation. This may take a minute....")
            mpeg_writer = animation.FFMpegWriter(fps=24, bitrate=1000,
                                                 codec="libx264", extra_args=["-pix_fmt", "yuv420p"])
            anim.save("{}{}{}x{}.mp4".format(self.media_filename, "_generation_", self.maze.num_rows,
                                           self.maze.num_cols), writer=mpeg_writer)

    def add_path(self):
        # Adding squares to animate the path taken to solve the maze. Also adding entry/exit text
        color_walls = "k"
        for i in range(self.maze.num_rows):
            for j in range(self.maze.num_cols):
                if self.show_text:
                    if self.maze.initial_grid[i][j].is_entry_exit == "entry":
                        self.ax.text(j*self.cell_size, i*self.cell_size, "START", fontsize = 7, weight = "bold")
                    elif self.maze.initial_grid[i][j].is_entry_exit == "exit":
                        self.ax.text(j*self.cell_size, i*self.cell_size, "END", fontsize = 7, weight = "bold")

                if self.maze.initial_grid[i][j].walls["top"]:
                    self.lines["{},{}: top".format(i, j)] = self.ax.plot([j*self.cell_size, (j+1)*self.cell_size],
                         [i*self.cell_size, i*self.cell_size], linewidth = 2, color = color_walls)[0]
                if self.maze.initial_grid[i][j].walls["right"]:
                    self.lines["{},{}: right".format(i, j)] = self.ax.plot([(j+1)*self.cell_size, (j+1)*self.cell_size],
                         [i*self.cell_size, (i+1)*self.cell_size], linewidth = 2, color = color_walls)[0]
                if self.maze.initial_grid[i][j].walls["bottom"]:
                    self.lines["{},{}: bottom".format(i, j)] = self.ax.plot([(j+1)*self.cell_size, j*self.cell_size],
                         [(i+1)*self.cell_size, (i+1)*self.cell_size], linewidth = 2, color = color_walls)[0]
                if self.maze.initial_grid[i][j].walls["left"]:
                    self.lines["{},{}: left".format(i, j)] = self.ax.plot([j*self.cell_size, j*self.cell_size],
                             [(i+1)*self.cell_size, i*self.cell_size], linewidth = 2, color = color_walls)[0]
                self.squares["{},{}".format(i, j)] = plt.Rectangle((j*self.cell_size,
                                                                    i*self.cell_size), self.cell_size, self.cell_size,
                                                                   fc = "red", alpha = 0.4, visible = False)
                self.ax.add_patch(self.squares["{},{}".format(i, j)])

    def animate_maze_solution(self):
        """Function that animates the process of generating the a maze where path is a list
        of coordinates indicating the path taken to carve out (break down walls) the maze."""

        # Create the figure and style the axes
        fig = self.configure_plot()

        # Adding indicator to see shere current search is happening.
        indicator = plt.Rectangle((self.maze.solution_path[0][0][0]*self.cell_size,
                                   self.maze.solution_path[0][0][1]*self.cell_size), self.cell_size, self.cell_size,
                                  fc="purple", alpha=0.6)
        self.ax.add_patch(indicator)

        self.add_path()

        def animate_squares(frame):
            """Function to animate the solved path of the algorithm."""
            if frame > 0:
                if self.maze.solution_path[frame - 1][1]:  # Color backtracking
                    self.squares["{},{}".format(self.maze.solution_path[frame - 1][0][0],
                                           self.maze.solution_path[frame - 1][0][1])].set_facecolor("orange")

                self.squares["{},{}".format(self.maze.solution_path[frame - 1][0][0],
                                       self.maze.solution_path[frame - 1][0][1])].set_visible(True)
                self.squares["{},{}".format(self.maze.solution_path[frame][0][0],
                                       self.maze.solution_path[frame][0][1])].set_visible(False)
            return []

        def animate_indicator(frame):
            """Function to animate where the current search is happening."""
            indicator.set_xy((self.maze.solution_path[frame][0][1] * self.cell_size,
                              self.maze.solution_path[frame][0][0] * self.cell_size))
            return []

        def animate(frame):
            """Function to supervise animation of all objects."""
            animate_squares(frame)
            animate_indicator(frame)
            self.ax.set_title("Step: {}".format(frame + 1), fontname = "serif", fontsize = 19)
            return []

        logging.debug("Creating solution animation")
        anim = animation.FuncAnimation(fig, animate, frames=self.maze.solution_path.__len__(),
                                       interval=100, blit=True, repeat=False)
        logging.debug("Finished creating solution animation")

        # Display the animation to the user
        plt.show()

        # Handle any saving
        if self.media_filename:
            print("Saving solution animation. This may take a minute....")
            mpeg_writer = animation.FFMpegWriter(fps=24, bitrate=1000,
                                                 codec="libx264", extra_args=["-pix_fmt", "yuv420p"])
            anim.save("{}{}{}x{}.mp4".format(self.media_filename, "_solution_", self.maze.num_rows,
                                           self.maze.num_cols), writer=mpeg_writer)
