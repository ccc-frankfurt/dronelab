from DoAgain import DoAgain
from djitellopy import Tello
import cv2
import pygame
import numpy as np
import pandas as pd
import time
import datetime

import os
import sys
import logging

from connectwifi import WifiFinder


class PadDrone(object):
    """ Contains the tello autonomous flight modes.

    """

    def __init__(self, args):
        # Parse arguements
        self.move_mode = args.move_mode
        self.display_stream = args.display_stream
        self.dryrun = args.dryrun
        self.save_stream = args.save_stream
        self.save_meta = args.save_meta
        self.ops_mode = args.ops_mode
        self.log_level = args.log_level
        self.path_to_data = '/home/pi/data/'
        self.fname_meta_global = 'meta_global.csv'  # filename for global metadata
        self.df_meta_global = []
        self.fname_meta_run = 'meta_run.csv'  # filename for temporal metadata for run
        self.df_meta_run = []  # pd.DataFrame(columns=['elapsed_time', 'frame', 'battery','temperature','flight_time','height','attitude','get_distance_tof','get_barometer'])
        self.speed = 10
        self.frames_to_save = {}

        self.path_to_log = '/var/log/dronelab'
        self.props_fly = args.props_fly
        self.prop_to_save = {}
        self.FPS = 1# TODO set to 1 while testing

        # internal
        self.send_rc_control = False

    def setup_logger(self):
        module = sys.modules['__main__'].__file__
        logfile = self.path_to_log + '/runDrone.log'
        logging.basicConfig(filename=logfile, format='%(asctime)s-%(process)d-%(name)s-%(levelname)s- %(message)s',
                            level=logging.DEBUG)
        logger = logging.getLogger(module)

        self.logger = logger

    def configure(self):

        self.setup_logger()
        self.logger.setLevel(self.log_level)

        self.is_conf_success = True
        # COnfigure:   cheh serial nr, chech battery status
        self.run_begin = datetime.datetime.now()
        self.run_begin_str = self.run_begin.strftime("%Y-%m-%d-%H-%M-%S")

        if not "DISPLAY" in os.environ:
            self.logger.debug("DISPLAY not set in environment")
            self.logger.debug("Setting Display  to :0.0")
            os.environ["DISPLAY"] = ":0.0"

        ##check for Wifi of Tello, if no existant exit, else connect
        self.tello_name = "TELLO-588A0C"  # Wifi to which tello will connect
        self.serial_number = self.tello_name  # serial_number for unique id of device, for tello drones take this

        password = ""
        self.wifi_interface_name = "wlan0"

        F = WifiFinder(server_name=self.tello_name,
                       password=password,
                       interface=self.wifi_interface_name
                       )
        conn_res = F.connect()
        self.F = F

        if not conn_res:
            self.logger.info("Could not connect to Tello Network.. exiting")
            self.is_conf_success = False
            return

        # Init Tello object that interacts with the Tello drone
        self.tello = Tello()

        try:
            self.tello.connect()
        except Exception as e:
            self.logger.info("Tello not connected,  closing  attempt to run... reason: " + str(e))
            self.is_conf_success = False
            return

        self.battery_initial = self.tello.get_battery()

        self.logger.debug("battery_initial " + str(self.battery_initial))

        self.temperature_initial = self.tello.get_temperature()

        try:
            self.temperature_initial = int(self.temperature_initial.split('~')[0])
        except:
            0
        self.logger.debug("temperature_initial" + str(self.temperature_initial))

        if self.temperature_initial > 93:
            self.logger.debug("Temperature to high > 93 stop configuring and exit....")
            return

        if self.save_stream or self.save_meta:
            self.save_stream_to = os.path.join(self.path_to_data, self.serial_number, self.run_begin_str)
            if not os.path.exists(self.save_stream_to):
                os.mkdir(self.save_stream_to)

        if self.display_stream:
            # Init pygame
            pygame.init()

            # Creat pygame window
            pygame.display.set_caption("Tello video stream")
            self.screen = pygame.display.set_mode([960, 720])
            pygame.time.set_timer(pygame.USEREVENT + 1, 50)

        self.sec_in_air_max = 10  ## Seconds in air after first frame of stream before going down (in startland mode)


        # Drone velocities between -100~100
        self.logger.info("Set speed to 0")
        self.set_vel_to0()

    def set_vel_to0(self):
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10

    def fps_waiter(self, elapsed_time):
        time.sleep(
            1 / self.FPS)  ## very coarse estimate time to wait by FPS -> get better calcualtion based on elapsed_time....

    def run(self):

        if not self.is_conf_success:
            self.logger.error("Configuration was not successfull.. exiting")
            return

        if not self.tello.set_speed(self.speed):
            self.logger.error("Not set speed to lowest possible")
            return

        # In case streaming is on. This happens when we quit this program without the escape key.
        if not self.tello.streamoff():
            self.logger.error("Could not stop video stream")
            return

        if not self.tello.streamon():
            self.logger.error("Could not start video stream")
            return

        if not self.tello.enable_mission_pads():
            self.logger.error("Could not enable mission pads")
            return

        frame_read = self.tello.get_frame_read()

        should_stop = False
        self.logger.info("Will fly in mode " + self.move_mode + "for seconds: " + str(self.sec_in_air_max))


            # Her beginn with frone flying  # use flight_time to sendnew commands in fixroute
        try:
            self.tello.takeoff()
        except Exception as Error:
            self.logger.error(Error)
            return
        # time.sleep(2)
        self.send_rc_control = True
        self.update()

        start_time = time.time()  #

        if self.save_meta:
            self.df_meta_global.append({'run_begin': self.run_begin_str,
                                        'serial_number': self.serial_number,
                                        'move_mode': self.move_mode,
                                        'route': "None",
                                        'battery_initial': self.battery_initial,
                                        'temperature_initial': self.temperature_initial,
                                        'sec_in_air_max': self.sec_in_air_max,
                                        'FPS': self.FPS,
                                        'flight_start_time': start_time})



        def log_information(counter):
            elapsed_time = time.time() - start_time
            self.logger.info(f"Elapsed time: {elapsed_time}") #TODO remove
            if frame_read.stopped:
                frame_read.stop()
                return

            frame_cv = cv2.cvtColor(frame_read.frame,
                                    cv2.COLOR_BGR2RGB)  # RGB_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            frame_cv_save = frame_cv.copy()
            frame_cv = np.rot90(frame_cv)
            frame_cv = np.flipud(frame_cv)

            if self.display_stream:
                self.screen.fill([0, 0, 0])
                frame = pygame.surfarray.make_surface(frame_cv)
                self.screen.blit(frame, (0, 0))
                pygame.display.update()

            if self.save_stream:
                filename = f"fps_{self.FPS}_frame_{counter:03}.jpg"

                if np.sum(frame_cv_save) != 0:
                    self.frames_to_save[filename] = frame_read.frame#frame_cv_save

            if self.save_meta:
                # self.tello.get_states()
                self.df_meta_run.append({'elapsed_time': elapsed_time,
                                         'frame': counter,
                                         'battery': self.tello.battery,
                                         'temperature': self.tello.temperature_highest,
                                         'flight_time': self.tello.flight_time,
                                         'height': self.tello.height,
                                         'pitch': self.tello.pitch,
                                         'roll': self.tello.roll,
                                         'yaw': self.tello.yaw,
                                         'get_distance_tof': self.tello.distance_tof,
                                         'get_barometer': self.tello.barometer})
            self.logger.info("elapsed_time since first frame " + str(elapsed_time) + " " + str(counter))

        # logging in subthread
        t = DoAgain(snapshots_interval=1.0/self.FPS, func=log_information)
        t.start()


        #hard coded route:
        # TODO add functionality add react to intput in realtime

        #TODO add serializable pad route: maybe like this:
        # csv := csv as String
        # route = PadRoute()
        # route.fromcsv(csv)
        # route.run(tello)
        # example command:"go_xyz_speed_yaw_mid,200,0,100,30,-90,1,2"
        try:
            # go_xyz_speed_yaw_mid(self, x, y, z, speed, yaw, mid1, mid2):
            #self.tello.go_xyz_speed_yaw_mid(200, 0, 100, 30, -90, 1, 2) ## sample run
            #self.tello.go_xyz_speed_yaw_mid(0, -80, 100, 30, -180, 2, 3)
            #self.tello.go_xyz_speed_yaw_mid(-200, 0, 100, 30, 90, 3, 4)
            #self.tello.go_xyz_speed_yaw_mid(0, 80, 100, 30, 0, 4, 1)

            speed = 30
            #
            self.tello.go_xyz_speed_yaw_mid(self, 0, 0, 100, speed, 0, 1, 1)
            self.tello.go_xyz_speed_mid(0, 0, 30, speed, 1)
            self.tello.go_xyz_speed_mid(280, 0, 30, speed, 1)
            self.tello.go_xyz_speed_yaw_mid(280, 0, 100, speed, 180, 1, 2)
            self.tello.go_xyz_speed_mid(0, 0, 30, speed, 2)
            self.tello.go_xyz_speed_mid(-280, 0, 30, speed, 2)
            self.tello.go_xyz_speed_yaw_mid(-280, 0, 100, speed, 180, 2, 1)
        except:
            self.logger.info("Run failed somehow")
        #finished


        try:
            self.tello.land()
        except:
            self.logger.info("landing failed..trying to save stream")

        t.stop()
        t.join()


        self.logger.info("Time to save stream after seconds: " + str(time.time() - start_time))
        self.logger.info("Saving stream to " + self.save_stream_to)

        if self.save_meta:
            pd.DataFrame(self.df_meta_run).to_csv(os.path.join(self.save_stream_to, self.fname_meta_run))
            pd.DataFrame(self.df_meta_global).to_csv(os.path.join(self.save_stream_to, self.fname_meta_global))
        if self.save_stream:
            for f, img in self.frames_to_save.items():
                cv2.imwrite(os.path.join(self.save_stream_to, f), img)
        self.logger.info("Saving of stream and metadaa finished")

        # res = self.F.protect_gateway_interface()
        # self.logger.info("Protecting against wlan gatewy interface switch:", res)
        if self.ops_mode:
            self.logger.info(
                'Wating for 2 Minutes to prevent another run within the next minute... Tello Drone will switch itselt off within 15 minutes.')
            time.sleep(2 * 60)

        # Call it always before finishing. To deallocate resources.
        self.tello.end()
        pygame.display.quit()

    def update(self):
        """ Update routine. Send velocities to Tello."""
        if self.send_rc_control:
            self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity, self.up_down_velocity,
                                       self.yaw_velocity)
