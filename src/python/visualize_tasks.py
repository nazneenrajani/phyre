"""
This is a file that includes code for taking a thrift represenation of a scene and generate a list of objects in that scene.

What do we care about?
# objects
Foreach object: type, x, y, radius, angle, color, height?, width?
	Jar: length of base and sides
"""

from collections import defaultdict
from math import sqrt

BODY_TYPE = {
    1 : "Static", 
    2 : "Dynamic"
}

COLOR_DICT = {
    0:"White",
    6:"Black",
    5:"Gray",
    2:"Green",
    3:"Blue",
    4:"Purple",
    1:"Red",
    7:"Light_red"
}

class output_object:

    def __init__(self, type, body, x, y, object_id):
        self._type = type # type of object (bar, circle, jar)
        self._state = BODY_TYPE[body.bodyType] # dynamic or static
        self._color = COLOR_DICT[body.color]
        self._x = x
        self._y = y
        self._object_id = object_id # a unique identifier for this object
    
    def get_short_description(self):
        return f"{self._state} {self._color} {self._type}"

    def print_description(self):
        raise NotImplementedError

class Jar (output_object):
    def __init__(self, body, object_id):
        x, y = body.position.x, body.position.y # this is the center of the base of the jar
        self._angle = body.angle # note this is in radians
        self._width = self.calculate_base_width(body) # assumption: that each bar has the same width
        
        self._baselen = self.calculate_base_length(body)
        self._sidelen = self.calculate_side_length(body)

        super().__init__("jar", body, x, y, object_id)

    # calculate the base length 
    def calculate_base_length(self, body):
        shapes = body.shapes
        base = shapes[0]
        top_right = base.polygon.vertices[0].x
        return abs(top_right) * 2

    # calculate the width of a bar
    def calculate_base_width(self, body):
        shapes = body.shapes
        base = shapes[0]
        top_right = base.polygon.vertices[0].y
        return abs(top_right) * 2

    # calculate the length of the bottom base of the Jar
    # Note: validation 
    # def calculate_base_length(self, body):
    #     lowest_y = min([vertex.y for bar in body.shapes for vertex in bar.polygon.vertices ]) # find the bottom line of the bottom bar
    #     lowest_x = float("inf")
    #     highest_x = float("-inf")
    #     for bar in body.shapes:
    #         for vertex in bar.polygon.vertices:
    #             if vertex.y == lowest_y:
    #                 lowest_x = min(lowest_x, vertex.x)
    #                 highest_x = max(highest_x, vertex.x)
    #     return highest_x - lowest_x

    # calculate the length of one of the arms of the jar
    # assumption: both arms are of the same length
    def calculate_side_length(self, body):

        leftmost_x = float("inf") # find the top left x
        lowest_y = float("inf") # find the bottom left y

        for bar in body.shapes:
            for vertex in bar.polygon.vertices:
                leftmost_x = min(leftmost_x, vertex.x)
                lowest_y = min(lowest_y, vertex.y)

        leftmost_x_y_value = float("-inf")
        lowest_y_x_value = float("inf")

        for bar in body.shapes:
            for vertex in bar.polygon.vertices:
                if vertex.x == leftmost_x: leftmost_x_y_value = max(leftmost_x_y_value, vertex.y)
                if vertex.y == lowest_y: lowest_y_x_value = min(lowest_y_x_value, vertex.x)

        x_base = leftmost_x - lowest_y_x_value
        y_height = leftmost_x_y_value - lowest_y

        return sqrt(x_base ** 2 + y_height ** 2)
        
    def print_description(self):
        print(f"ID: {self._object_id}| {self._state} {self._color} {self._type} at ({self._x:.2f}, {self._y:.2f}) at a {self._angle:.2f} degree angle with a leg length of {self._sidelen:.2f}, base length of {self._baselen:.2f}, and width of {self._width:.2f}")

class Bar (output_object):
    def __init__(self, body, object_id):
        vertices = body.shapes[0].polygon.vertices
        self._length = abs(vertices[0].x) * 2
        self._width = abs(vertices[0].y) * 2
        self._angle = body.angle

        super().__init__("bar" if object_id >=4 else "boundary", body, body.position.x, body.position.y, object_id)

    def print_description(self):
        print(f"ID: {self._object_id}| {self._state} {self._color} {self._type} at ({self._x:.2f}, {self._y:.2f}) at a {self._angle:.2f} degree angle with a length of {self._length:.2f} and width of {self._width:.2f}")

class Circle (output_object):
    def __init__(self, body, object_id):
        self._radius = body.shapes[0].circle.radius

        super().__init__("circle", body, body.position.x, body.position.y, object_id)

    def print_description(self):
        print(f"ID: {self._object_id}| {self._color} {self._type} at ({self._x:.2f}, {self._y:.2f}) with a radius of {self._radius:.2f}")

# special class for user input circles
class UserCircle ():
    def __init__(self, circle_object, id):
        self._x = circle_object.position.x
        self._y = circle_object.position.y
        self._radius = circle_object.radius
        self._object_id = id
        self._color = "Red"
        self._state = "Dynamic"
        self._type = "User Circle" # make this one?
    
    def get_short_description(self):
        return f"{self._state} {self._color} {self._type}"

    def print_description(self):
        print(f"ID: {self._object_id}| {self._color} {self._type} at ({self._x:.2f}, {self._y:.2f}) with a radius of {self._radius:.2f}")

# returns a list of objects in the scene
def create_list_of_objects(thrift_scene):
    # print(thrift_scene)
    bodies = thrift_scene.bodies
    object_list = []
    count = 0 # TODO: until IDs decided, this is a temporary item ID

    for body in bodies:
        # print(body)

        # JAR
        if len(body.shapes) == 3:
            object_list.append(Jar(body, count))

        # CIRCLE
        elif body.shapes[0].circle:
            object_list.append(Circle(body, count))

        # BAR
        else:
            object_list.append(Bar(body, count))

        count += 1

    return object_list

# add user input independently from the inital scene
def add_user_ball(thrift_scene, user_input):
    thrift_scene.append(UserCircle(user_input.balls[0], 1.1))

# print all objects
def print_scene(scene_dict):
    for obj in scene_dict:
        obj.print_description()

import json

# creates a json representation of the initialobject list
def initial_json(simulation_number, action, scene_dict):
    
    # [object_id, type, state, color, x, y, angle, length, width, base_length, radius, isuserinput]
    json_obj_list = []
    for obj in scene_dict:
        curr_object = {}
        curr_object["object_id"] = obj._object_id
        curr_object["type"] = obj._type
        curr_object["state"] = obj._state
        curr_object["color"] = obj._color
        curr_object["x"] = obj._x
        curr_object["y"] = obj._y
        curr_object["angle"] = obj._angle if isinstance(obj, Jar) or isinstance(obj, Bar) else None
        curr_object["length"] = obj._length if isinstance(obj, Bar) else obj._sidelen if isinstance(obj, Jar) else None
        curr_object["width"] = obj._width if isinstance(obj, Jar) or isinstance(obj, Bar) else None
        curr_object["base_length"] = obj._baselen if isinstance(obj, Jar) else None
        curr_object["radius"] = obj._radius if isinstance(obj, Circle) or isinstance(obj, UserCircle) else None
        json_obj_list.append(json.dumps(curr_object))

    
    objects_json_list = "[" + ",".join(json_obj_list) + "]"
    action = [str(x) for x in action]
    action_str = "[" + ",".join(action) + "]"
    return '[{"task_id": ' + '"' + str(simulation_number) + '"' + \
        ', "action": ' + action_str + \
        ', "objects": ' + objects_json_list + '}]'

import csv
def initial_csv_with_sim_col(initial_json):
    # create columns for the csv
    task_id = initial_json[0]["task_id"]
    action = initial_json[0]["action"]
    object_keys = list(initial_json[0]["objects"][0].keys())
    key_names = ["task_id"] + ["action"] + object_keys

    # create the rows in the csv
    new = []
    for objects in initial_json[0]["objects"]:
        temp = {}
        temp["task_id"] = task_id
        temp["action"] = action
        for key in object_keys:
            temp[key] = objects[key]
        new.append(temp)

    # Actually write to the csv
    f = open("initial_out.csv", "w")
    output = csv.writer(f)
    output.writerow(key_names)
    for row in new:
        output.writerow(row.values())
    
    f.close()

def initial_csv(initial_json, file_name):
    # create columns for the csv
    object_keys = list(initial_json[0]["objects"][0].keys())

    # create the rows in the csv
    new = []
    for objects in initial_json[0]["objects"]:
        temp = {}
        for key in object_keys:
            if key == "object_id" and objects["type"] == "User Circle":
                temp[key] = max(initial_json[0]["objects"], key=lambda x: x["object_id"])["object_id"] + 1
            else:
                temp[key] = objects[key]
        new.append(temp)

    # Actually write to the csv
    f = open(file_name, "w")
    output = csv.writer(f)
    output.writerow(object_keys)
    for row in new:
        output.writerow(row.values())
    f.close()