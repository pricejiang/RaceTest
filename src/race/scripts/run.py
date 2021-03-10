import os
import sys
# import argparse

import subprocess
# from subprocess import DEVNULL, STDOUT, check_call
import os, signal
import random
import carla
import numpy as np
import rospy
from graic_msgs.msg import WaypointInfo

four_wheel_vehicle = ['vehicle.audi.a2','vehicle.tesla.model3','vehicle.bmw.grandtourer','vehicle.audi.etron','vehicle.seat.leon','vehicle.mustang.mustang','vehicle.tesla.cybertruck','vehicle.lincoln.mkz2017','vehicle.lincoln2020.mkz2020','vehicle.dodge_charger.police','vehicle.audi.tt','vehicle.jeep.wrangler_rubicon','vehicle.chevrolet.impala','vehicle.nissan.patrol','vehicle.nissan.micra','vehicle.mercedesccc.mercedesccc','vehicle.mini.cooperst','vehicle.chargercop2020.chargercop2020','vehicle.toyota.prius','vehicle.mercedes-benz.coupe','vehicle.citroen.c3','vehicle.charger2020.charger2020']
two_wheel_vehicle = ['vehicle.bh.crossbike','vehicle.kawasaki.ninja','vehicle.gazelle.omafiets','vehicle.yamaha.yzf','vehicle.harley-davidson.low_rider','vehicle.diamondback.century']

car_name_prefix = 'hero'

class CommandNode:
    def __init__(self, N, log, track, model_type, num_wheels, set_spectator=False):
        self.N = N 
        self.log = log 
        self.track = track 
        self.model_type = model_type
        self.num_wheels = num_wheels
        self.set_spectator = set_spectator
        self.vehicles = {}

        if self.set_spectator:
            self.setSpectator()
        
        self.spawnCars()

    def waypointCallback(self, data):
        role_name = data.role_name 
        reachFinal = data.reachedFinal
        self.vehicles[role_name]['finished'] = reachFinal

    def setSpectator(self):
        client = carla.Client('localhost', 2000)
        world = client.get_world()
        spectator = world.get_spectator()
        center = np.mean([v['init_pose'][:3] for v in vehicles], axis=0)
        transform = carla.Transform(carla.Location(x=center[0], y=-center[1], z=center[2] + 40),
                                    carla.Rotation(pitch=-89, yaw=-62.5))
        spectator.set_transform(transform)

    def spawnCars(self):
        for i in range(self.N):
            # in .launch file: spawn vehicle, control bridge, perception module
            v = {}

            v['launch_log'] = self.log+'/hero%d_launch_log.txt'%i

            role_name = car_name_prefix + str(i)
            v['role_name'] = role_name

            with open('objects.json.template', 'r') as f:
                obj = f.read()
            obj = obj.replace('[[role_name]]', role_name)

            if self.model_type != "model_free" and model_type != "model_based":
                rospy.logwarn("Wrong choice of model type %s; use model_free as default"%self.model_type)
                model_type = "model_free"
            
            if self.model_type == "model_based" and self.track == "t2_triple":
                rospy.logerr("Please don't chooce model_based vehicle when running track2")
                raise rospy.exceptions.ROSInterruptException
            
            if self.model_type == "model_free":
                v['model_free'] = 1
            else:
                v['model_free'] = 0

            if self.track == "t1_triple":
                init_pose = [164,11+i*10,4,0,0,-180]
            elif self.track == "t2_triple":
                init_pose = [95.5,107+i*10,4,0,0,-136]
            v['init_pose'] = init_pose
            obj = obj.replace('[[spawn_point]]', '"x": %f, "y": %f, "z": %f, "roll": %f, "pitch": %f, "yaw": %f'%tuple(init_pose))

            if self.num_wheels == 4 or model_type=="model_based":
                vehicle = random.choice(four_wheel_vehicle)
            elif self.num_wheels == 2:
                vehicle = random.choice(two_wheel_vehicle)
            else:
                rospy.logerr("Wrong choice of number of wheels %s"%self.num_wheels)
            
            obj = obj.replace('[[vehicle]]', vehicle)

            json_file = '/tmp/objects_%s.json'%role_name
            v['json_file'] = json_file
            with open(v['json_file'], 'w') as f:
                f.write(obj)

            v['finished'] = False

            cmd = ('roslaunch race spawn_vehicle.launch config_file:=%s role_name:=%s track:=%s model_free:=%s &> %s')%tuple([v['json_file'], v['role_name'], self.track, v['model_free'], v['launch_log']])
            # The os.setsid() is passed in the argument preexec_fn so
            # it's run after the fork() and before  exec() to run the shell.
            v['proc_handler'] = subprocess.Popen(cmd, preexec_fn=os.setsid, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

            rospy.Subscriber('/carla/%s/waypoints'%role_name, WaypointInfo, self.waypointCallback)
            self.vehicles[role_name] = v

    def shut_down(self):
        import rosnode 
        # for v in self.vehicles.values():
        #     os.killpg(os.getpgid(v['proc_handler'].pid), signal.SIGTERM)  # Send the signal to all the process groups
        names = rosnode.get_node_names()
        rosnode.kill_nodes(names)

    def checkFinish(self):
        count = 0
        for role_name in self.vehicles:
            if self.vehicles[role_name]['finished']:
                count += 1
        if count == self.N:
            self.shut_down()
    
def run(cn):
    rate = rospy.Rate(10)
    rospy.on_shutdown(cn.shut_down)

    while not rospy.is_shutdown():
        cn.checkFinish()
        rate.sleep()

if __name__ == '__main__':
    rospy.init_node('CommandNode', disable_signals=True)
    N = rospy.get_param("~N", 1)
    log = rospy.get_param("~log", '/tmp/')
    track = rospy.get_param("~track", "t1_triple")
    model_type = rospy.get_param("~model_type", "model_free")
    num_wheels = rospy.get_param("~num_wheels", 4)
    os.chdir(os.path.dirname(__file__))
    cwd = os.getcwd()
    import time
    time.sleep(10)
    try: 
        cn = CommandNode(N, log, track, model_type, num_wheels)
        run(cn)
    except rospy.exceptions.ROSInterruptException:
        rospy.loginfo("CommandNode shut down")