#!/usr/bin/env python

#  data_dump dumps wifi scans into a csv file.
#  Copyright (C) 2013  Rafael Berkvens rafael.berkvens@ua.ac.be
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import rospy
from wifi_scan.msg import Fingerprint
from std_msgs.msg import Header
import tf2_ros

lista_mac = []


def fingerprintCallback(fingerprint, args):
  f_h = args[0]
  f_d = args[1]
  tfBuffer = args[2]
  data = dict()

  try:
    trans = tfBuffer.lookup_transform("map", 'base_footprint', rospy.Time())
    x = trans.transform.translation.x
    y = trans.transform.translation.y
    z = trans.transform.rotation.z
  except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
    rospy.loginfo(rospy.get_name() + ": Exception")

  #f.write(str(fingerprint.header.stamp) + ',')
  for address_rssi in fingerprint.list:
    data[address_rssi.address] = address_rssi.rssi
    if address_rssi.address not in lista_mac:
        lista_mac.append(address_rssi.address)
        rospy.loginfo(rospy.get_name() + ": Dodano adres do listy: " + address_rssi.address)
        string = address_rssi.address
        string += ','
        f_h.write(string)

  string = '{},{},{},'.format(x, y, z)
  for address in lista_mac:
    string += str(data.get(address, ""))
    string += ','
  f_d.write(string)
  f_d.write('\n')

def groundTruthCallback(data, f):
  rospy.loginfo(rospy.get_name() + ": I heard something")
  f_d.write(str(data.stamp) + ',' + data.frame_id)
  f_d.write('\n')

def data_dump():
  rospy.init_node('data_dump')

  f_h = open('HEADER.csv', 'w')
  f_d = open('DATA.csv', 'w')
  f_h.write('')
  f_d.write('')
  f_h.close()
  f_d.close()
  f_h = open('HEADER.csv', 'a')
  f_d = open('DATA.csv', 'a')
  string = "x,y,z,"
  f_h.write(string)

  tfBuffer = tf2_ros.Buffer()
  listener = tf2_ros.TransformListener(tfBuffer)

  rospy.Subscriber("/wifi_fp", Fingerprint, fingerprintCallback, [f_h, f_d,tfBuffer])
  rospy.Subscriber("/gt_nfc", Header, groundTruthCallback, [f_h, f_d])
  rospy.spin()


if __name__ == '__main__':
  data_dump()
