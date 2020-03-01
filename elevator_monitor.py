'''
Visualizes multiple elevators and their states
and draws the ENTIRE screen with ELEVATORS from LEFT to RIGHT
'''
import tkinter as tk
from constants import ElevatorDoorStatus, ElevatorDirection
from elevator import Elevator
from multiple_elevator_controller import MultipleElevatorController

LEVELS = "G 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15".split()

ELEVATOR_FRAME_WIDTH = 170
ELEVATOR_MARGIN = 70
ELEVATOR_WIDTH = 18
ELEVATOR_HEIGHT = 24
# Gap between elevator text labels
ELEVATOR_LABEL_VERTICAL_GAP = 14

CANVAS_HEIGHT = ELEVATOR_HEIGHT * (len(LEVELS) + 2) + ELEVATOR_MARGIN * 2
REFRESH_INTERVAL = 800


class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.create_elevators()
        self.master = master
        self.pack()
        self.create_widgets()
        self.create_canvas()
        self.step_forward()

    def create_widgets(self):
        tk.Label(self, text="Current Level")

        self.call_level = tk.StringVar(self)
        self.call_level.set(LEVELS[0])

        call_label = tk.Label(self, text="Call A Lift")
        call_label.grid(row=0, column=0)

        # Dropdown of levels to seleect
        current_level = tk.OptionMenu(self, self.call_level, *LEVELS)
        current_level.grid(row=0, column=1)

        # Elevator UP / DOWN call buttons
        up_button = tk.Button(self, text="UP", fg="black",
                              command=self.call_elevator_up)
        up_button.grid(row=0, column=2)
        down_button = tk.Button(self, text="DOWN", fg="black",
                                command=self.call_elevator_down)
        down_button.grid(row=0, column=3)

        # Quit Button
        quit = tk.Button(self, text="QUIT", fg="red",
                          command=self.master.destroy)
        quit.grid(row=0, column=4)

        # Create some quick debug controls for each visual elevator
        for i in range(len(self.controller.elevators)):
            elevator_label = tk.Label(self, text="Elevator {0}: ".format(i))
            elevator_label.grid(row=i+1, column=0)

            level_selection = tk.StringVar(self)
            level_selection.set(LEVELS[0])

            test = tk.OptionMenu(self, level_selection, *LEVELS)
            test.grid(row=i+1, column=1)

            # Function wrapper that just simulates somebody
            # in the lift selecting a level
            def activate_elevator(i, level_selection):
                return lambda: self.controller.elevators[i].select_level(
                    LEVELS.index(level_selection.get()))

            # Create a visual button to select a level
            select_button = tk.Button(
                self, text="Select Level", fg="black",
                command=activate_elevator(i, level_selection)
            )
            select_button.grid(row=i+1, column=2)

    def create_elevators(self):
        ''' Initialize our elevators for use in this visualisation  '''
        self.controller = MultipleElevatorController()
        self.controller.elevators.append(Elevator(LEVELS))
        self.controller.elevators.append(Elevator(LEVELS))
        self.controller.elevators.append(Elevator(LEVELS))

    def call_elevator_up(self):
        ''' Call any elevator to come UP to our level '''
        self.call_elevator(ElevatorDirection.UP)

    def call_elevator_down(self):
        ''' Call any elevator to come DOWN to our level '''
        self.call_elevator(ElevatorDirection.DOWN)

    def call_elevator(self, direction):
        ''' Call / summon an elevator to our level  '''
        from_level = LEVELS.index(self.call_level.get())
        self.controller.call_elevator(from_level, direction)

    def create_canvas(self):
        ''' Create our canvas to hold all our elevators visually '''
        canvas_width = len(self.controller.elevators) * ELEVATOR_FRAME_WIDTH
        canvas_height = CANVAS_HEIGHT
        self.canvas = tk.Canvas(self.master,
                                width=canvas_width,
                                height=canvas_height)
        self.canvas.pack()
        self.draw_elevators()

    def draw_elevators(self):
        ''' Draw each elevator onto the canvas '''
        for i, elevator in enumerate(self.controller.elevators):
            self.draw_elevator(elevator, left=ELEVATOR_FRAME_WIDTH * i)

    def step_forward(self):
        ''' Simulate time by stepping each elevator to its next command '''
        self.controller.step_forward()
        self.canvas.delete("all")
        self.draw_elevators()
        self.master.after(REFRESH_INTERVAL, self.step_forward)

    def draw_elevator(self, elevator, left=0):
        '''
        Draw a visual representation of an elevator.
        Its just a rectangle with a line through it.
        Include our status information at the bottom
        '''
        w = self.canvas
        base_y = CANVAS_HEIGHT - ELEVATOR_MARGIN
        elevator_x = ELEVATOR_MARGIN + left

        # If door is closed draw GREY, otherwise BLACK
        if elevator.door_status == ElevatorDoorStatus.CLOSED:
            fill = "#476042"
        else:
            fill = "#000000"

        # Create elevator rectangle
        w.create_rectangle(
            elevator_x,
            base_y - ELEVATOR_HEIGHT * (elevator.current_level + 1),
            elevator_x + ELEVATOR_WIDTH,
            base_y - ELEVATOR_HEIGHT * (elevator.current_level),
            fill=fill,
        )

        text_font = "Times 13 bold"
        text_color = "black"

        # Include our elevator STATUS info
        gap = ELEVATOR_LABEL_VERTICAL_GAP
        self.canvas.create_text(
            elevator_x + ELEVATOR_WIDTH // 2,
            base_y - ELEVATOR_HEIGHT * (elevator.current_level) + gap,
            fill=text_color, font=text_font,
            text=f"Level: {elevator.current_level}"
        )
        self.canvas.create_text(
            elevator_x + ELEVATOR_WIDTH // 2,
            base_y - ELEVATOR_HEIGHT * (elevator.current_level) + gap * 2,
            fill=text_color, font=text_font,
            text=f"Door Status: {elevator.door_status.value}"
        )
        self.canvas.create_text(
            elevator_x + ELEVATOR_WIDTH // 2,
            base_y - ELEVATOR_HEIGHT * (elevator.current_level) + gap * 3,
            fill=text_color, font=text_font,
            text=f"Direction: {elevator.direction.value}"
        )
        self.canvas.create_text(
            elevator_x + ELEVATOR_WIDTH // 2,
            base_y - ELEVATOR_HEIGHT * (elevator.current_level) + gap * 4,
            fill=text_color, font=text_font,
            text=f"Status: {elevator.status.value}"
        )

        # If the door is closed draw a line through it
        if elevator.door_status == ElevatorDoorStatus.CLOSED:
            LINE_WIDTH = 2
            w.create_line(
                elevator_x + ELEVATOR_WIDTH//2,
                base_y - ELEVATOR_HEIGHT * (elevator.current_level + 1),
                elevator_x+ ELEVATOR_WIDTH//2,
                base_y - ELEVATOR_HEIGHT * (elevator.current_level),
                fill="#111111", width=LINE_WIDTH)


root = tk.Tk()
app = Application(master=root)
app.mainloop()
