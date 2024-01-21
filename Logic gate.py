import math
from PIL import ImageTk
from tkinter import *

# declaration of constants
window = Tk()
W = 1920
H = 1080
GATE_Y = 990
GATE_X_OFFSET = 165
GATE_BAR_Y = H - 137
BG_COLOUR = '#282828'
BUTTON_COLOUR = '#454545'
# declaration of all global variables
Gates = []
Lines = []
layers = []
Ovals = []
Input_instances = []
Output_instances = []
Mouse_drag = False
Is_minimized = False


class Gate:
    def __init__(self, root, x, y, image, type_of_gate, gate_num):
        self.output_lines = []
        self.root = root
        self.image = image
        self.type_of_gate = str(type_of_gate)
        # Gate_num is used to figure out whether the gate is the gate in the
        # gate bar at the bottom or the screen or not
        self.gate_num = gate_num
        self.x = self.root.canvasx(x)
        self.y = self.root.canvasy(y)
        # Create label and window objects for the gate images Labels are
        # placed inside the window objects so if the window object moves the
        # label also moves
        self.label = Label(self.root, image=self.image, bg=BG_COLOUR)
        self.window = self.root.create_window(self.x, self.y, window=self.label, tag='GATE')
        self.selected = False
        # Bind left mouse button,left mouse button release and motion of the mouse to their appropriate methods
        # This is done for both the label and the window objects
        self.root.tag_bind(self.window, '<Button-1>', self.on_press)
        self.label.bind('<Button-1>', self.on_press)
        self.root.tag_bind(self.window, '<ButtonRelease-1>', self.on_release)
        self.label.bind('<ButtonRelease-1>', self.on_release)
        self.root.tag_bind(self.window, '<B1-Motion>', self.on_move)
        self.label.bind('<B1-Motion>', self.on_move)
        self.root.tag_bind(self.window, '<Button-3>', self.delete_gate)
        self.label.bind('<Button-3>', self.delete_gate)
        # places 2 inputs for all gates besides the NOT gate
        if self.type_of_gate != 'NOT':
            self.input1 = Gate_input_node(self.x, self.y, 1, self.root, self, 'GATE')
            self.input2 = Gate_input_node(self.x, self.y, 2, self.root, self, 'GATE')
            self.output = Gate_output_node(self.x, self.y, self.root, self, 'GATE')
        else:
            self.input1 = Gate_input_node(self.x, self.y, 1, self.root, self, 'NOT')
            self.output = Gate_output_node(self.x, self.y, self.root, self, 'NOT')

    def update_line(self):
        # Updates the colour of all output lines coming out of the gate
        # output node depending on the colour of the output node
        for line in self.output_lines:
            colour = self.output.get_colour()
            if colour == 'red':
                line.change_colour('red')
            elif colour == 'lightgrey':
                line.change_colour('grey')

    def get_coords_of_inputs(self):
        # Returns the coordinates of the input node(s) depending on if the
        # gate is a NOT gate or not
        try:
            coords = [self.input1.get_coords(), self.input2.get_coords()]
            return coords
        except:
            return [self.input1.get_coords()]

    def append_output_line(self, line):
        self.output_lines.append(line)

    def update_gate(self):
        # Updates the colour of the output node based on the inputs and gate
        # type
        original = self.root.itemcget(self.output.gate_node, 'fill')
        if self.type_of_gate != 'NOT':  # Main function for most gates besides
            # the NOT gate
            bit1 = self.root.itemcget(self.input1.gate_node, 'fill')
            bit2 = self.root.itemcget(self.input2.gate_node, 'fill')
            bits = [bit1, bit2]  # Array storing the 2 colours of the 2 inputs
            # Function name is the same as the gate type name so globals
            # can be used
            function_to_call = globals()[self.type_of_gate]
            for index, bit in enumerate(bits):  # Changes the colours in the array to integers
                # either 0 or 1
                if bit == 'red':
                    bits[index] = 1
                else:
                    bits[index] = 0
            result = function_to_call(bits[0], bits[1])  # Calls one of the global OR,XOR etc. functions
            if result == 1:
                self.root.itemconfig(self.output.gate_node, fill='red')
            else:
                self.root.itemconfig(self.output.gate_node, fill='lightgrey')
        else:  # Conditions if the gate is a NOT gate
            bit = self.root.itemcget(self.input1.gate_node, 'fill')
            if bit == 'red':
                self.root.itemconfig(self.output.gate_node, fill='lightgrey')
            else:
                self.root.itemconfig(self.output.gate_node, fill='red')
        if original != self.root.itemcget(self.output.gate_node, 'fill'):
            # Updates the colour of all output lines coming out of the gate
            # (if they are any) if the colour of the
            # output node changed colour
            self.update_line()
            for line in self.output_lines:
                line.update_line_input()  # Updates the colour of the oval the  # line is connected to at the other end
        else:
            pass

    def on_press(self, event):  # This function runs when the user left clicks any
        # gate
        global mouse_drag
        mouse_drag = True
        self.selected = True
        self.offset_x = event.x
        self.offset_y = event.y
        # Saves original coordinates of the gate in case it will be needed to
        # be moved back because of an invalid position
        self.original_x = self.x + event.x - self.offset_x
        self.original_y = self.y + event.y - self.offset_y
        # This creates a new gate under the gate that has been clicked if the
        # gate is the original in the gate bar at the bottom of the screen
        if self.gate_num == 1:
            self.new_gate = Gate(self.root, self.x, self.y, self.image, self.type_of_gate, 1)
            global Gates
            Gates.append(self)
            self.gate_num = 0

    def on_release(self, event):  # This is run when the user releases their
        # left mouse button if they clicked a gate
        global mouse_drag
        mouse_drag = False
        self.selected = False
        self.check_gate_pos()
        Update()

    def move_gate_back(self):  # Moves gate back to the position it was dragged
        # from if the position is invalid
        self.move_gate(self.original_x, self.original_y)

    def check_gate_pos(self):  # Checks if the gate is outside the valid region
        x = self.root.canvasx(self.label.winfo_x())
        y = self.root.canvasy(self.label.winfo_y())
        if self.type_of_gate != 'NOT':  # Different region for the NOT gate as
            # the NOT gate is smaller
            if x <= 91 or x >= 1705:
                self.on_move(None)
            if y <= 28 or y >= 835:
                self.on_move(None)
        else:
            if x <= 93 or x >= 1670:
                self.on_move(None)
            if y <= 29 or y >= 849:
                self.on_move(None)

    def move_gate(self, x, y):  # Moves gate,gate nodes and all wires connected
        # to the gate back to their porper position
        self.root.coords(self.window, x, y)
        self.x = x
        self.y = y
        if self.type_of_gate != 'NOT':
            for line in Lines:
                if self.input1.get_coords() == line.get_coords():
                    line_to_update_1 = line
                if self.input2.get_coords() == line.get_coords():
                    line_to_update_2 = line
            self.input1.place_node(x, y)
            self.input2.place_node(x, y)
        else:
            # The for loop gets the instance(s) of the connection class to update if the coordinates of the input node
            # is the same as the end x and y for the line
            for line in Lines:  # Lines is a global list that stores all the wires on the canvas
                if self.input1.get_coords() == line.get_coords():
                    line_to_update_1 = line
            self.input1.place_node(x, y)
        self.output.place_node(x, y)
        # Moves the input lines to their positions if there are any lines connected else it passes
        try:
            line_to_update_1.update_line(self.input1.get_coords()[0], self.input1.get_coords()[1], 'IN')
        except NameError:
            pass
        try:
            line_to_update_2.update_line(self.input2.get_coords()[0], self.input2.get_coords()[1], 'IN')
        except NameError:
            pass
        # Moves all output lines if there are any coming out of the gate output node to their respected positions
        for line in self.output_lines:
            line.update_line(self.output.get_coords()[0], self.output.get_coords()[1], 'OUT')

    def on_move(self, event):  # Runs if the gate has been left-clicked by the user, the user is holding down their left
        # mouse button and the position of their cursor is changing
        if self.selected:
            # if statement used to fix refresh rate issue as sometimes the gate can follow the user's
            # cursor a split second after the user releases their left mouse button
            x = self.x + event.x - self.offset_x
            y = self.y + event.y - self.offset_y
        else:
            x = self.original_x
            y = self.original_y
        self.move_gate(x, y)

    def delete_gate(self, event):  # Deletes the gate, gate nodes and all lines connected to the gate if the user
        # right-clicks the gate
        if self.gate_num != 1:  # Only deletes the gate if the gate is not in the gate bar
            lines_to_delete = []
            self.root.delete(self.window)
            self.input1.destroy()
            self.output.destroy()
            if self.type_of_gate != 'NOT':
                self.input2.destroy()
            for line in Lines:  # Gets all lines connected to the input nodes and stores the instances of the
                # connection class in the lines_to_delete list
                input1_coords = self.input1.get_coords()
                try:
                    input2_coords = self.input2.get_coords()
                except AttributeError:
                    input2_coords = None
                if input1_coords == line.get_coords() or input2_coords == line.get_coords():
                    lines_to_delete.append(line)
            for line in lines_to_delete:  # Deletes all the lines in the list
                line.delete_line('e')
            for line in self.output_lines:
                line.delete_line('e')
            for instance in Output_instances:  # Updates all output main bulbs on the red bar on the right side of the screen
                instance.update()
        else:
            pass


class Gate_input_node:
    def __init__(self, x, y, input_num, root, parent, type):
        self.parent = parent
        self.input = input_num
        if type == 'NOT':  # the offset for x and y is the position the input node should be in relation to the
            # centre of the image. The NOT gate as only 1 input, so it will have different offsets.
            self.offset_y = 0
            self.offset_x = 75
        else:
            if self.input == 1:  # The top input node for each gave is input 1 and the bottom input is input 2
                self.offset_x = 92
                self.offset_y = -19.5
            else:
                self.offset_x = 92
                self.offset_y = 19.5
        self.x = x - self.offset_x
        self.y = y + self.offset_y
        self.root = root
        self.radius = 10
        self.gate_node = self.root.create_oval(self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius, fill='lightgrey',
                                               tags='INPUT_BULB_GATE')
        self.root.tag_raise(self.gate_node)  # Puts the node to the top layer, so it appears above all wires

    def destroy(self):  # Deletes the node from the canvas
        self.root.delete(self.gate_node)

    def place_node(self, x, y):  # Places note in position provided also considering the offsets
        self.x = x - self.offset_x
        self.y = y + self.offset_y
        self.root.coords(self.gate_node, self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius)

    def get_coords(self):  # Getter function that returns the current x and y centre coordinates of the node
        return self.x, self.y

    def get_oval(self):  # A getter function that returns the tkinter oval object
        return self.gate_node

    def get_colour(self):  # A getter function that returns the current colour of
        # the input node
        colour = self.root.itemcget(self.gate_node, 'fill')
        return colour


class Gate_output_node(Gate_input_node):  # Inherits Gate_input_node methods
    def __init__(self, x, y, root, parent, type):
        super().__init__(x, y, None, root, parent, type)
        self.offset_x = 75 if type == 'NOT' else 90
        self.x = x + self.offset_x
        self.y = y
        self.line = None
        self.gate_node = self.root.create_oval(self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius, fill='lightgrey',
                                               tags='OUTPUT_BULB_GATE')
        # Binds the output node to mouse buttons so the user can draw a wire out of the output node
        self.root.tag_bind(self.gate_node, "<Button-1>", self.start_draw)
        self.root.tag_bind(self.gate_node, "<B1-Motion>", self.draw)
        self.root.tag_bind(self.gate_node, "<ButtonRelease-1>", self.check_valid_line_pos)
        Ovals.append(self)

    def check_valid_line_pos(self, e):
        global Mouse_drag
        Mouse_drag = False
        valid = self.line.check_pos()  # check_pos method is called in the Connection class
        if valid:
            self.parent.append_output_line(self.line)  # Appends the Connection class instance to output lines attribute
            # in the gate class
            self.parent.update_line()  # Updates the colour of the line to the colour of the output node
            layers.append(self)
        else:
            pass

    def start_draw(self, event):  # Called when the user left-clicks their left mouse button on the output node
        # Draws line with the same colour as the output node and raises the node above the line, so it looks nicer
        global Mouse_drag
        Mouse_drag = True
        colour = self.root.itemcget(self.gate_node, 'fill')
        self.line = Connection(self.x, self.y, event.x, event.y, self.root, colour, self)
        self.root.tag_raise(self.gate_node)

    def draw(self, event):  # Called when the user clicks the output node, holds their left mouse button and moves their mouse
        self.line.change_coords(event.x, event.y)
        self.root.tag_raise(self.gate_node)

    def place_node(self, x, y):  # Polymorphism method of the super class method, places node with centre coords provided
        self.x = x + self.offset_x
        self.y = y
        self.root.coords(self.gate_node, self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius)

    def append_line(self, line):  # Appends the supplied line to the parent class output_lines list and the global layers list
        self.parent.append_output_line(line)
        layers.append(self)

    def check(self, x, y):  # This method checks if the line being drawn out of the output node is trying to be
        # connected to the gate's own input
        coords = self.parent.get_coords_of_inputs()
        for pair in coords:
            if pair[0] == x and pair[1] == y:
                return True  # True means that the wire is trying to be connected to the gates own input
        return False


class Main_bulb:
    def __init__(self, root, x, y, type, colour):
        self.lines = []
        self.ovals = []
        self.root = root
        self.radius = 20
        self.type = type
        self.line_counter = 0
        self.radius_check = 20
        self.x = 51.5 if type == 'INPUT_BULB' else x if type == 'INTERSECTION' else 1876.5
        self.y = y
        self.overlap = False
        self.colour = 'green' if type == 'INPUT_BULB' else colour if type == 'INTERSECTION' else 'red'
        self.main_bulb = self.root.create_oval(self.x - self.radius, y - self.radius, self.x + self.radius, y + self.radius,
                                               fill=BG_COLOUR if self.type != 'INTERSECTION' else self.colour, width=3, outline=self.colour, tag=str(type))
        for item in self.root.find_withtag(str(type)):
            if item != self.main_bulb and self.root.type(item) == 'oval':
                x2, y2, self.radius_check = self.root.coords(item)[0] + self.radius, self.root.coords(item)[1] + self.radius_check, self.radius
                distance = math.sqrt((x2 - self.x) ** 2 + (y2 - self.y) ** 2)  # Calculates the distance between the 2
                # if an oval was found using pythagoras
                if distance <= self.radius * 2:
                    self.overlap = True
                    break
        if not self.overlap:
            self.root.lift(self.main_bulb)
            self.root.tag_bind(self.main_bulb, "<Button-1>", self.start_draw)
            self.root.tag_bind(self.main_bulb, "<B1-Motion>", self.draw)
            self.root.tag_bind(self.main_bulb, "<ButtonRelease-1>", self.check_valid_line_pos)
            if self.type == 'INTERSECTION' or self.type == 'OUTPUT_BULB':
                pass
            else:
                self.root.tag_bind(self.main_bulb, "<Button-3>", self.change_input)
            self.root.focus_set()
            self.root.tag_bind(self.main_bulb, '<Enter>', self.makebind)
            self.root.tag_bind(self.main_bulb, '<Leave>', self.delbind)
            self.line = None
        else:
            self.root.delete(self.main_bulb)

    def get_overlap(self):  # Returns the boolean attribute overlap
        return self.overlap

    def change_colour(self, colour):  # Changes the colour of the main bulb depending on the colour provided and the
        # type of the main bulb
        if self.type == 'OUTPUT_BULB':
            if colour == 'red':
                self.root.itemconfig(self.main_bulb, fill='red')
            else:
                self.root.itemconfig(self.main_bulb, fill=BG_COLOUR)
        elif self.type == 'INTERSECTION':
            self.root.itemconfig(self.main_bulb, fill=colour, outline=colour)
            for line in self.lines:
                line.change_colour(colour)
        else:
            try:
                self.root.itemconfig(self.line, str(colour))
            except:
                pass
            Update()

    def delbind(self, e):
        self.root.unbind('<q>')
        self.root.unbind('<Q>')

    def makebind(self, e):  # Binds the canvas to q and Q to delete the main bulb. This bind is only active when the
        # user is hovering over the main_bulb
        global Mouse_drag
        if not Mouse_drag:
            self.root.bind('<q>', self.delete_bulb)
            self.root.bind('<Q>', self.delete_bulb)

    def delete_bulb(self, event):  # Deletes the main bulb as well as all the lines connected to it if the main bulb
        # is not an intersection
        for line in self.lines:
            line.delete_line(None)
        if self.type == 'OUTPUT_BULB':
            global Output_instances
            Output_instances.remove(self)
        if self.root.find_withtag(CURRENT) and float(self.root.itemcget(CURRENT, 'width')) == 3.0:
            self.root.delete(CURRENT)
        elif self.type == 'INTERSECTION':
            self.root.delete(self.main_bulb)
        Update()

    def check_valid_line_pos(self, e):  # calls the check_pos() method in the connection class on the line which has
        # been drawn by the user. This runs when the user releases their left mouse button
        global Mouse_drag
        Mouse_drag = False
        valid = self.line.check_pos()
        if valid:
            self.lines.append(self.line)
            if len(self.lines) == 2 and self.type == 'OUTPUT_BULB':  # Extra check to see if a line is already connected
                # to an output bulb
                self.line.delete_line('e')
                self.lines.pop()
            else:
                oval = self.line.oval
                if oval == None:
                    pass
                else:
                    self.ovals.append(oval)
        else:
            pass
        Update()

    def start_draw(self, event):  # Runs when the user left-clicks the main bulb
        global Mouse_drag
        Mouse_drag = True
        colour = self.root.itemcget(self.main_bulb, "fill")
        self.line = Connection(self.x, self.y, event.x, event.y, self.root, colour, self)
        self.root.tag_raise(self.main_bulb)

    def draw(self, event):  # Changes end x and y points of the line which is being currently drawn by the user to the
        # x and y of the user's mouse cursor's coordinates
        self.line.change_coords(event.x, event.y)
        self.root.tag_raise(self.main_bulb)

    def change_input(self, e):  # Changes the signal sent by the input main bulb when the user right-clicks it
        colour = self.root.itemcget(self.main_bulb, "fill")
        if colour == 'red':
            self.root.itemconfig(self.main_bulb, fill=BG_COLOUR)
            for line in self.lines:
                line.change_colour('bg_colour')
            for oval in self.ovals:
                self.root.itemconfig(oval, fill='lightgrey')
        else:
            self.root.itemconfig(self.main_bulb, fill="red")
            for line in self.lines:
                line.change_colour('red')
            for oval in self.ovals:
                self.root.itemconfig(oval, fill='red')
        Update()

    def delete_oval(self, input_oval):  # deletes the supplied oval from the ovals attribute list
        self.ovals.remove(input_oval)

    def get_colour(self):  # returns the colour of the main bulb
        return self.root.itemcget(self.main_bulb, 'fill')

    def get_type(self):  # returns type of the main bulb either Input,Output or Intersection
        return self.type

    def get_oval(self):  # returns the tkinter oval object (the main bulb)
        return self.main_bulb

    def get_centre_coords(self):  # returns the current centre coordinates of the main bulb
        try:
            oval_coords = self.root.coords(self.main_bulb)  # this method returns the bounding box of the oval (x1,y1,x2,y2)
            center_coords = [(oval_coords[0] + oval_coords[2]) / 2, (oval_coords[1] + oval_coords[3]) / 2]
        except:
            return 0
        return center_coords

    def set_counter(self, counter):
        self.line_counter = int(counter)

    def get_counter(self):
        return self.line_counter

    def set_oval(self, oval):
        self.ovals.append(oval)

    def delete_line(self,line):
        self.lines.remove(line)

    def update(self):  # It checks if there are any lines connected to the main bulb if not the fill of the main_bulb is
        # switched to grey (this method is only used by the output bulb so intersections and input bulbs will not be
        # switched to 'off' if they have no lines coming out of them)
        for line in Lines:
            centre_coords = self.get_centre_coords()
            x = line.get_coords()[0]
            y = line.get_coords()[1]
            if centre_coords[0] == x and centre_coords[1] == y:
                if line not in self.lines:
                    self.lines.append(line)
                    break
        if len(self.lines) == 0 or self.line_counter == 0:
            self.root.itemconfig(self.main_bulb, fill=BG_COLOUR)


class Connection:
    def __init__(self, s_x, s_y, x, y, root, colour, instance_input):
        self.instance_input = instance_input
        self.root = root
        self.intersections = []
        self.start_x = s_x
        self.start_y = s_y
        self.end_x = x
        self.end_y = y
        self.snap_distance = False
        # Creation of the line hitbox is so that the user does not need to perfectly click on the thin line to delete it
        self.line_hitbox = self.root.create_line(self.start_x, self.start_y, self.end_x, self.end_y, width=10, fill=BG_COLOUR, tag='LINE_HITBOX')
        if colour == 'red':
            self.colour = 'red'
        else:
            self.colour = 'grey'
        self.line = self.root.create_line(self.start_x, self.start_y, self.end_x, self.end_y, width=3, fill=self.colour, tags='LINE')
        self.root.tag_bind(self.line, "<Button-3>", self.delete_line)
        self.root.tag_bind(self.line_hitbox, "<Button-3>", self.delete_line)
        self.root.tag_bind(self.line, "<Button-1>", self.create_intersection)
        self.root.tag_bind(self.line_hitbox, "<Button-1>", self.create_intersection)
        self.root.tag_bind(self.line_hitbox, "<Enter>", self.makebind)
        self.root.tag_bind(self.line, "<Leave>", self.delbind)

    def delbind(self, e):
        self.root.unbind("<Q>")
        self.root.unbind("<q>")

    def makebind(self, e):
        global mouse_drag
        if not mouse_drag:
            self.root.bind("<q>", self.delete_line)
            self.root.bind("<Q>", self.delete_line)

    def create_intersection(self, e):  # Creates a new instance of the main bulb class with they type as Intersection
        intersection = Main_bulb(self.root, e.x, e.y, 'INTERSECTION', self.root.itemcget(self.line, 'fill'))
        self.intersections.append(intersection)
        try:
            self.instance_input.set_oval(intersection.get_oval())
        except AttributeError:
            pass

    def change_coords(self, x, y):
        snap_distance = 40
        try:
            # If the line is being drawn from the output main bulb it can only snap to output nodes of logic gates
            # else the line can snap and be placed only on input nodes of gates and output main bulbs
            if self.instance_input.get_type() != 'OUTPUT_BULB':
                ovals = self.root.find_withtag('INPUT_BULB_GATE') + self.root.find_withtag('OUTPUT_BULB')
            else:
                ovals = self.root.find_withtag('OUTPUT_BULB_GATE')
        except:
            ovals = self.root.find_withtag('INPUT_BULB_GATE') + self.root.find_withtag('OUTPUT_BULB')
        for oval in ovals:
            # Calculates the distance between the user's cursor and the snap-able ovals and if they distance is less
            # than the snap distance the line will automatically snap to that oval else the line end point will appear
            # on the tip of user's pointer
            oval_coords = self.root.coords(oval)
            center_coords = ((oval_coords[0] + oval_coords[2]) / 2, (oval_coords[1] + oval_coords[3]) / 2)
            distance = math.sqrt((x - center_coords[0]) ** 2 + (y - center_coords[1]) ** 2)
            if distance < snap_distance:
                self.root.coords(self.line_hitbox, (self.start_x, self.start_y, center_coords[0], center_coords[1]))
                self.root.coords(self.line, (self.start_x, self.start_y, center_coords[0], center_coords[1]))
                self.end_x = center_coords[0]
                self.end_y = center_coords[1]
                self.root.tag_raise('INPUT_BULB_GATE')
                self.root.tag_raise('OUTPUT_BULB')
                self.root.tag_raise('OUTPUT_BULB_GATE')
                self.snap_distance = True
                self.oval = oval
                break
            else:
                self.root.coords(self.line_hitbox, (self.start_x, self.start_y, x, y))
                self.root.coords(self.line, (self.start_x, self.start_y, x, y))
                self.oval = None
                self.end_x = x
                self.end_y = y
                self.snap_distance = False

    def update_line(self, x, y, type):  # Moves the end or start point of the line to the specified x and y coordinates
        # based on the type of line. This method is only called when the user clicks and drags a gate with connected
        # wires'
        for intersection in self.intersections:  # All intersection points get deleted when the line moves as there is
            # a scaling issue with tkinter when trying to move an oval object in relation to the line length and
            # position
            intersection.delete_bulb(None)
        try:
            if self.output_instance.get_type() == 'OUTPUT_BULB':
                self.end_y = y
                self.end_x = x
                self.root.coords(self.line, self.start_x, self.start_y, float(x), float(y))
                self.root.coords(self.line_hitbox, self.start_x, self.start_y, float(x), float(y))
                return
        except:
            pass
        if type == 'IN':
            self.end_y = y
            self.end_x = x
            self.root.coords(self.line, self.start_x, self.start_y, float(x), float(y))
            self.root.coords(self.line_hitbox, self.start_x, self.start_y, float(x), float(y))
        elif type == 'OUT':
            self.start_x = x
            self.start_y = y
            self.root.coords(self.line, x, y, self.end_x, self.end_y)
            self.root.coords(self.line_hitbox, x, y, self.end_x, self.end_y)

    def get_coords(self):
        return self.end_x, self.end_y

    def change_colour(self, colour):  # Changes colour of the line and its intersections based on conditions and supplied colour
        if colour == 'red':
            self.root.itemconfig(self.line, fill='red')
        else:
            self.root.itemconfig(self.line, fill='grey')
        for intersection in self.intersections:
            intersection.change_colour(self.root.itemcget(self.line, 'fill'))

    def delete_line(self, e):  # Deletes the line and hitbox. Also updates all attributes and variables the line might
        # of been stored in
        try:
            if type(self.output_instance).__name__ == "Main_bulb":  # sets the counter of the main bulb output instance to 0 if the line does connect to the main bulb output
                self.set_counter(0)
            else:
                pass
        except:
            pass
        self.root.delete(self.line_hitbox)
        self.root.delete(self.line)
        try:
            try:  # If the line was not connected to an output main bulb the bulb will turn 'off'
                tag = self.root.gettags(self.oval)
            except:
                tag = None
            if tag[0] == 'OUTPUT_BULB':
                pass
            elif tag != None and self.root.itemcget(self.oval, 'fill') == 'red':
                self.root.itemconfig(self.oval, fill='lightgrey')
        except:
            pass
        try:
            self.output_instance.delete_line(self)
        except:
            pass
        try:  # deletes the oval the line is connected to from the main bulb class instance it is dragged from
            self.instance_input.delete_oval(self.oval)
            self.oval = None
        except:
            self.oval = None
        for intersection in self.intersections:  # deletes all intersections on the line if there are any
            intersection.delete_bulb(None)
        try:
            Lines.remove(self)  # removes its own instance of its own class from the global variable list Lines
        except ValueError:
            pass
        Update()

    def update_line_input(self):  # Updates the colour of the line and the oval it is connected to based on the colour
        # of the oval it is connected from
        colour = self.instance_input.get_colour()
        if colour != 'red':
            self.root.itemconfig(self.line, fill='grey')  # Changes colour of line
            try:  # Changes colour of the oval it connects to if there is one
                if self.root.gettags(self.oval)[0] == 'OUTPUT_BULB':
                    self.root.itemconfig(self.oval, fill=BG_COLOUR)
                else:
                    self.root.itemconfig(self.oval, fill='lightgrey')
            except:
                pass
        else:  # changes the colour of the oval the line is connected to, to red and any intersection points to red also
            self.root.itemconfig(self.oval, fill='red')
        for intersection in self.intersections:
            intersection.change_colour(self.root.itemcget(self.line, 'fill'))

    def check_pos(self):  # checks if the line is in a valid position
        all_lines = self.root.find_withtag('LINE')
        for n in range(len(all_lines)):  # checks if there is already a line with the same end point if so the position
            # is invalid
            x1, y1, x2, y2 = self.root.coords(all_lines[n])
            if self.line != all_lines[n] and self.end_x == x2 and self.end_y == y2:
                self.delete_line(None)
                return False
            else:
                pass
        if type(self.instance_input).__name__ == "Gate_output_node":  # checks if the line being drawn out of the output
            # gate node is trying to be connected back into the gate's own input if so the position is invalid
            connected_to_self = self.instance_input.check(self.end_x, self.end_y)
            if connected_to_self:
                self.delete_line(None)
                return False
        if not self.snap_distance:  # if the line didn't snap to a valid oval the line is invalid
            self.delete_line(None)
            return False
        if self.get_counter() == 1 and self.root.gettags(self.oval)[0] == 'OUTPUT_BULB':  # checks if there is
            # already a line connected to the output main bulb if so the position is invalid
            self.delete_line(None)
            return False
        else:  # extra conditions if the line was dragged out of the output main node to any gate output node
            if self.root.gettags(self.oval)[0] == 'OUTPUT_BULB_GATE':
                for oval in Ovals:  # updates the colour of the output main bulb to the colour of the connected node
                    if oval.get_oval() == self.oval:
                        oval.append_line(self)  # appends the line instance to the instance of the gate_output_node
                        # class as the line is counted as a 'output' line going from the gate's output, but it was
                        # drawn by the user the other way round
                        if oval.get_colour() == 'red':
                            self.root.itemconfig(self.line, fill='red')
                        else:
                            self.root.itemconfig(self.line, fill='grey')
                        # switches the position of the ovals meaning that the output gate node is the node that the line
                        # is 'coming from' and it's going to the output main bulb even though it was drawn the other way
                        self.instance_input.change_colour(self.root.itemcget(self.line, 'fill'))
                        self.set_counter(1)  # sets counter of the output main bulb instance to 1
                        self.oval = self.instance_input.get_oval()
                        self.instance_input = oval
            else:  # updates the colour of the connected oval if the line is not drawn to the output bulb main bulb
                colour = self.root.itemcget(self.line, 'fill')
                if colour != 'red':
                    self.root.itemconfig(self.oval, fill='lightgrey')
                else:
                    self.root.itemconfig(self.oval, fill=colour)
            Lines.append(self)
            self.set_counter(1)
            Update()
            return True

    def set_counter(self, counter):  # changes the counter attribute in the main bulb output class
        global Output_instances
        for instance in Output_instances:
            center_coords = instance.get_centre_coords()
            if self.start_x == center_coords[0] and self.start_y == center_coords[1]:
                instance.set_counter(counter)
                self.output_instance = instance
                break
            elif self.end_x == center_coords[0] and self.end_y == center_coords[1]:
                instance.set_counter(counter)
                self.output_instance = instance
                break

    def get_counter(self):  # returns the counter of the output main bulb instance the line is connected of if the line
        # is in fact connected to an output main bulb
        try:
            return self.output_instance.get_counter()
        except:
            return 0


# global logic functions that take in 2 integers '0 or 1' and return 1 integer either 0 or 1
def OR(bit1, bit2):
    output = int(bit1 | bit2)
    return output


def NOR(bit1, bit2):
    output = int(not (bit1 | bit2))
    return output


def AND(bit1, bit2):
    output = int(bit1 & bit2)
    return output


def NAND(bit1, bit2):
    output = int(not (bit1 & bit2))
    return output


def XOR(bit1, bit2):
    output = int(bit1 ^ bit2)
    return output


def XNOR(bit1, bit2):
    output = int(not (bit1 ^ bit2))
    return output


def EnterButton(e):  # procedure is run when the user's cursor goes into the quit button bounding box
    widget = e.widget
    widget.configure(cursor='hand2', bg='#656565')  # changes look of cursor and highlights the button if the user is  # hovering over it


def LeaveButton(e):  # turns the quit back to its original state when the user goes out of the bounding box
    widget = e.widget
    widget.configure(bg='#454545')


def Place_in_out(e, type, root):  # places the input or output main bulbs when the user clicks on either the green or red bars
    # respectively or close to the bars
    x = root.canvasx(e.x) if str(e.widget)[1:len(str(e.widget))] == '!canvas' else e.x + 55
    y = root.canvasy(e.y) if str(e.widget)[1:len(str(e.widget))] == '!canvas' else e.y + 45
    if type == 'OUT' or (x in range(1876 - 40, 1876 + 40) and y in range(40, H - 180)):  # checks if the bulb will be
        # in the valid x and y ranges
        output = Main_bulb(root, None, y, 'OUTPUT_BULB', None)
        if not output.get_overlap():
            Output_instances.append(output)
    elif x in range(10, 90) and y in range(40, H - 180):
        input = Main_bulb(root, None, y, 'INPUT_BULB', None)
        if not input.get_overlap():
            Input_instances.append(input)
    else:
        pass


def Update():  # updates the colours of all of the lines,gates,main bulbs etc.
    for n in range(0, len(layers) + 1):  # updates every new layer(I called a layer when a wire is drawn out of a gate's
        # output node it's a layer as it adds a new layer of gate(s) the signal has to get through
        for line in Lines:
            line.update_line_input()
        for gate in Gates:
            gate.update_gate()
        try:  # updates all the output main bulbs if there are any
            for instance in Output_instances:
                instance.update()
        except:
            pass

def toggle_fullscreen():
    if window.attributes('-fullscreen'):
        window.attributes('-fullscreen', False)
    else:
        window.attributes('-fullscreen', True)

def minimize_window():
    global Is_minimized
    Is_minimized = True
    window.iconify()
    toggle_fullscreen()


def restore_window(event):
    global Is_minimized
    if Is_minimized:
        Is_minimized= False
        window.attributes('-fullscreen', True)
        window.deiconify()

def show_text():
    Icon_img = PhotoImage(file='Images/Icon.png')
    info_window = Toplevel(window)
    info_window.attributes('-topmost', True)
    info_window.configure(bg=BG_COLOUR)
    info_window.title('Controls')
    window.iconbitmap('Images/Icon.ico')
    text_label = Label(info_window, text="LEFT CLICK + DRAG = Drags gate or draws wire \n LEFT CLICK = To place input,output or intersection \n RIGHT CLICK = To "
                                         "deletes gate or change state of input bulb \n 'Q' - To delete a wire,input,output or intersection ", bg=BG_COLOUR,
                       fg='white',font=('Helvetica',10,'bold') , pady=10,padx=10)
    text_label.pack()

def Initialize():
    # loads all images into memory
    Icon_img = PhotoImage(file='Images/Icon.png')
    OR_img = ImageTk.PhotoImage(file='Images/OR.png')
    NOR_img = ImageTk.PhotoImage(file='Images/NOR.png')
    AND_img = ImageTk.PhotoImage(file='Images/AND.png')
    NAND_img = ImageTk.PhotoImage(file='Images/NAND.png')
    XOR_img = ImageTk.PhotoImage(file='Images/XOR.png')
    XNOR_img = ImageTk.PhotoImage(file='Images/XNOR.png')
    NOT_img = ImageTk.PhotoImage(file='Images/NOT(126x69).png')
    # creates and places all initial tkinter objects
    window.iconbitmap('Images/Icon.ico')
    window.geometry(f'{W}x{H}')
    window.configure(bg=BG_COLOUR)
    window.attributes('-fullscreen', True)

    Gate_main = Canvas(window, bg=BG_COLOUR, width=W, height=H, highlightthickness=0)
    Gate_main.place(x=0, y=0)
    Gate_main.create_line(0, 920, 1920, 920, width=5, fill='grey')

    input_bar = Canvas(Gate_main, bg='green', width=5, height=870, highlightthickness=0)
    input_bar.place(x=50, y=43)

    FuncBar_frame = LabelFrame(window, bg='#141414', width=W, height=30, padx=1, pady=1, bd=0)
    FuncBar_frame.place(x=0, y=0)
    FuncBar_frame.pack_propagate(False)

    output_bar = Canvas(Gate_main, bg='red', width=5, height=870, highlightthickness=0)
    output_bar.place(x=1875, y=43)

    Button_quit = Button(FuncBar_frame, text='X', command=window.quit, height=1, width=6, bd=0, bg=BUTTON_COLOUR, font=('Helvetica',10,'bold'),fg='white')
    Button_quit.pack(side='right')

    Button_minmise = Button(FuncBar_frame, text='—', command=minimize_window, height=1, width=6, bd=0, bg=BUTTON_COLOUR, font=('Helvetica',10,'bold'),fg='white')
    Button_minmise.pack(side = 'right')

    Infobutton = Button(FuncBar_frame, text="Controls", command=show_text, height=1, width=8, bd=0, bg=BUTTON_COLOUR, font=('Helvetica',10,'bold'),fg='white')
    Infobutton.pack(side = 'right')

    Title = Label(FuncBar_frame, text='Logic Gate Sim', height=1, width=14, bd=0, bg='#141414', font=('Helvetica',10,'bold'), fg = 'white')
    Title.pack(side='left')

    Gate_names = ['AND', 'NAND', 'OR', 'NOR', 'NOT', 'XOR', 'XNOR']

    for index, name in enumerate(Gate_names):  # places all the gate name under the gate images
        var_name = name + 'label'
        globals()[var_name] = Label(window, text='yes', bg=BG_COLOUR, fg='white', font=('Helvetica', 15,'bold'))
        globals()[var_name].configure(text=str(name))
        globals()[var_name].place(x=165 + (index) * 250, y=1040)

    # places all initial gates in the gate bar at the bottom of the screen
    Gate(Gate_main, 50 + GATE_X_OFFSET, GATE_Y, AND_img, 'AND', 1)
    Gate(Gate_main, 300 + GATE_X_OFFSET, GATE_Y, NAND_img, 'NAND', 1)
    Gate(Gate_main, 550 + GATE_X_OFFSET, GATE_Y, OR_img, 'OR', 1)
    Gate(Gate_main, 800 + GATE_X_OFFSET, GATE_Y, NOR_img, 'NOR', 1)
    Gate(Gate_main, 1050 + GATE_X_OFFSET, GATE_Y + 6, NOT_img, 'NOT', 1)
    Gate(Gate_main, 1300 + GATE_X_OFFSET, GATE_Y, XOR_img, 'XOR', 1)
    Gate(Gate_main, 1550 + GATE_X_OFFSET, GATE_Y, XNOR_img, 'XNOR', 1)
    # binds the quit button as well as the main canvas, the input and output bars to their appropriate functions
    input_bar.bind('<Button-1>', lambda event: Place_in_out(event, 'IN', Gate_main))
    output_bar.bind('<Button-1>', lambda event: Place_in_out(event, 'OUT', Gate_main))
    Gate_main.bind('<Button-1>', lambda event: Place_in_out(event, 'TYPE', Gate_main))
    Button_quit.bind('<Enter>', EnterButton)
    Button_quit.bind('<Leave>', LeaveButton)
    Button_minmise.bind('<Enter>', EnterButton)
    Button_minmise.bind('<Leave>', LeaveButton)
    Infobutton.bind('<Enter>', EnterButton)
    Infobutton.bind('<Leave>', LeaveButton)
    window.bind("<Map>", restore_window)

Initialize()

window.mainloop()
