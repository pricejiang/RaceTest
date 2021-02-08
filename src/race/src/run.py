import os
import sys
import argparse

import subprocess
# from subprocess import DEVNULL, STDOUT, check_call
import os, signal

parser = argparse.ArgumentParser(description="")
parser.add_argument('-N', type=int, default='3')
parser.add_argument('--log', type=str, default='/tmp/')

args = parser.parse_args()

vehicles = []
for i in range(args.N):
    # in .launch file: spawn vehicle, control bridge, perception module
    v = {}

    v['launch_log'] = args.log+'/vehicle-%d_launch_log.txt'%i

    role_name = 'vehicle-%d'%i
    v['role_name'] = role_name

    with open('objects.json.template', 'r') as f:
        obj = f.read()
    obj = obj.replace('[[role_name]]', role_name)
    json_file = '/tmp/objects_%s.json'%role_name
    v['json_file'] = json_file

    with open(v['json_file'], 'w') as f:
        f.write(obj)

    init_pose = [-17+i*5,-132,0,0,0,180]
    v['init_pose'] = init_pose

    cmd = ('roslaunch spawn_vehicle.launch config_file:=%s role_name:=%s spawn_point:=' + ','.join(['%f',]*6) + ' &> %s')%tuple([v['json_file'], v['role_name'],]+*(v['init_pose'])+[v['launch_log'],])
    # The os.setsid() is passed in the argument preexec_fn so
    # it's run after the fork() and before  exec() to run the shell.
    v['proc_handler'] = subprocess.Popen(cmd, preexec_fn=os.setsid, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

# rospy.init_node('RaceMain')
# rate = rospy.Rate(100)  # 100 Hz    

# # subscribe to positions
# while not rospy.is_shutdown():
#     rate.sleep()

# for i in range(args.N):
#     os.killpg(os.getpgid(v['proc_handler'].pid), signal.SIGTERM)  # Send the signal to all the process groups