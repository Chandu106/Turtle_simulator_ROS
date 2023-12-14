import rclpy
from rclpy.node import Node
from functools import partial
import random
import math

from turtlesim.srv import Spawn
from my_robot_interfaces.msg import Turtle 
from my_robot_interfaces.msg import TurtleArray

class TurtleSpawner(Node):
    def __init__(self):
        super().__init__("turtle_spawner")
        self.turtle_counter = 1
        self.turtle_name_prefix = "turtle"
        self.alive_turtles = []
        self.alive_turtles_publisher = self.create_publisher(TurtleArray, "alive_turtles", 10)
        self.spawn_turtle_timer = self.create_timer(2.0, self.spawn_new_turtle)
    
    def publish_alive_turtles(self):
        msg = TurtleArray()
        msg.turtles = self.alive_turtles
        self.alive_turtles_publisher.publish(msg)

    def spawn_new_turtle(self):
        self.turtle_counter += 1
        name = self.turtle_name_prefix + str(self.turtle_counter)
        x = random.uniform(0.0, 11.0)
        y = random.uniform(0.0, 11.0)
        theta = random.uniform(0.0, 2*math.pi)
        self.call_spawn_server(name, x, y, theta)
    
    def call_spawn_server(self, turtle_name, x, y, theta):
        client = self.create_client(Spawn, "spawn")
        while not client.wait_for_service(1.0):
            self.get_logger().warn("waiting for server...")

        request = Spawn.Request()
        request.x = x
        request.y = y
        request.theta = theta
        request.name = turtle_name

        future = client.call_async(request)
        future.add_done_callback(partial(self.callback_call_spawn, turtle_name = turtle_name, x = x, y = y, theta = theta))

    def callback_call_spawn(self, future, turtle_name, x, y, theta):
        try:
            response = future.result()
            if response.name!= "":
                self.get_logger().info("Turle " + response.name + "is now alive")
                new_turtle = Turtle()
                new_turtle.name = response.name 
                new_turtle.x = x 
                new_turtle.y = y 
                new_turtle.theta = theta 
                self.alive_turtles.append(new_turtle)
                self.publish_alive_turtles()

        except Exception as e:
            self.get_logger().error("Service call failed %r" % (e,)) 


def main(args=None):
    rclpy.init(args=args)
    node = TurtleSpawner()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "main":
    main()