#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
from styx_msgs.msg import Lane, Waypoint
from scipy.spatial import KDTree
import numpy as np
import math

'''
This node will publish waypoints from the car's current position to some `x` distance ahead.

As mentioned in the doc, you should ideally first implement a version which does not care
about traffic lights or obstacles.

Once you have created dbw_node, you will update this node to use the status of traffic lights too.

Please note that our simulator also provides the exact location of traffic lights and their
current status in `/vehicle/traffic_lights` message. You can use this message to build this node
as well as to verify your TL classifier.

TODO (for Yousuf and Aaron): Stopline location for each traffic light.
'''

LOOKAHEAD_WPS = 20 # Number of waypoints we will publish. You can change this number


class WaypointUpdater(object):
    def __init__(self):
        rospy.init_node('waypoint_updater', log_level = rospy.INFO)

        rospy.Subscriber('/current_pose', PoseStamped, self.pose_cb)
        rospy.Subscriber('/base_waypoints', Lane, self.waypoints_cb)

        # TODO: Add a subscriber for /traffic_waypoint and /obstacle_waypoint below

	#rospy.loginfo("INIIIIIIIIIIIIIIIIIIIT")
        self.final_waypoints_pub = rospy.Publisher('final_waypoints', Lane, queue_size=1)

        # TODO: Add other member variables you need below
	self.base_waypoints = None
	self.pose  = None
	self.waypoints_2d = None
	self.kd_tree = None
#        rospy.spin()
	rate = rospy.Rate(50)
	while not rospy.is_shutdown():
	    #if not self.kd_tree:
	#	rospy.loginfo("Nooooooooooooooooooooo tree")
	    if self.base_waypoints and self.pose and self.kd_tree:
	 #       rospy.loginfo("set")
	        self.set_final_waypoints()
	  #  if not self.base_waypoints:
	   #     rospy.loginfo("NOOOOOOOOOOOOOO waypoints")
	   # if not self.pose:
	    #    rospy.loginfo("NOOOOOOOOOOOOOOOO pose")
	    rate.sleep()

    def pose_cb(self, msg):
        # TODO: Implement

	self.pose = msg
	
	
    def waypoints_cb(self, waypoints):
        # TODO: Implement
	#rospy.loginfo("waypoints_cb")
        self.base_waypoints = waypoints
	if not self.waypoints_2d:
	    self.waypoints_2d = [[waypoint.pose.pose.position.x, waypoint.pose.pose.position.y] for waypoint in waypoints.waypoints]
	   # rospy.loginfo(len(self.waypoints_2d))
	    self.kd_tree = KDTree(self.waypoints_2d)
	    #self.kd_tree = KDTree([[0,1],[1,2]])
	   # rospy.loginfo(type(self.kd_tree))


    def find_waypoint_ahead(self):
	dist,ind = self.kd_tree.query([self.pose.pose.position.x,self.pose.pose.position.y])
	direction_waypoint = np.array([self.waypoints_2d[ind][0]-self.pose.pose.position.x,self.waypoints_2d[ind][1]-self.pose.pose.position.y])
	heading_direction = np.array([self.pose.pose.orientation.x, self.pose.pose.orientation.y])
	if np.dot(direction_waypoint,heading_direction)<0:
           ind +=1 #perhaps mod total number of waypoints
	   ind %=len(self.waypoints_2d)
	return ind

    def set_final_waypoints(self):
	ind  = self.find_waypoint_ahead()
	#final_waypoints_pub = self.base_waypoints[ind:ind+LOOKAHEAD_WPS]
	lane = Lane()
	lane.header = self.base_waypoints.header
	lane.waypoints = self.base_waypoints.waypoints[ind:ind+LOOKAHEAD_WPS]
	self.final_waypoints_pub.publish(lane)

    def traffic_cb(self, msg):
        # TODO: Callback for /traffic_waypoint message. Implement
	pass

    def obstacle_cb(self, msg):
        # TODO: Callback for /obstacle_waypoint message. We will implement it later
        pass

    def get_waypoint_velocity(self, waypoint):
        return waypoint.twist.twist.linear.x

    def set_waypoint_velocity(self, waypoints, waypoint, velocity):
        waypoints[waypoint].twist.twist.linear.x = velocity

    def distance(self, waypoints, wp1, wp2):
        dist = 0
        dl = lambda a, b: math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2  + (a.z-b.z)**2)
        for i in range(wp1, wp2+1):
            dist += dl(waypoints[wp1].pose.pose.position, waypoints[i].pose.pose.position)
            wp1 = i
        return dist


if __name__ == '__main__':
    try:
        WaypointUpdater()
    except rospy.ROSInterruptException:
        rospy.logerr('Could not start waypoint updater node.')
