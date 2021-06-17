from djitellopy import TelloNew, BackgroundFrameRead
import cv2
import pygame
import numpy as np
import pandas as pd
import time
import datetime
import argparse
import os,sys
import logging
from shutil import copyfile
from connectwifi import WifiFinder
from datetime import datetime
# Speed of the drone
S = 60
# Frames per second of the pygame window display
FPS = 25


class FrontEnd(object):
    """ Maintains the Tello display and moves it through the keyboard keys.
        Press escape key to quit.
        The controls are:
            - T: Takeoff
            - L: Land
            - Arrow keys: Forward, backward, left and right.
            - A and D: Counter clockwise and clockwise rotations
            - W and S: Up and down.
    """

    def __init__(self):
        # Init pygame
        pygame.init()

        # Creat pygame window
        pygame.display.set_caption("Tello video stream")
        self.screen = pygame.display.set_mode([960, 720])

        # Init Tello object that interacts with the Tello drone
        self.tello = TelloNew()

        # Drone velocities between -100~100
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10

        self.send_rc_control = False

        # create update timer
        pygame.time.set_timer(pygame.USEREVENT + 1, 50)

    def run(self):

        if not self.tello.connect():
            print("Tello not connected")
            return

        if not self.tello.set_speed(self.speed):
            print("Not set speed to lowest possible")
            return

        # In case streaming is on. This happens when we quit this program without the escape key.
        if not self.tello.streamoff():
            print("Could not stop video stream")
            return

        if not self.tello.streamon():
            print("Could not start video stream")
            return

        frame_read = self.tello.get_frame_read()

        should_stop = False
        while not should_stop:

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.update()
                elif event.type == pygame.QUIT:
                    should_stop = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        should_stop = True
                    else:
                        self.keydown(event.key)
                elif event.type == pygame.KEYUP:
                    self.keyup(event.key)

            if frame_read.stopped:
                frame_read.stop()
                break

            self.screen.fill([0, 0, 0])
            frame = cv2.cvtColor(frame_read.frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = np.flipud(frame)
            frame = pygame.surfarray.make_surface(frame)
            self.screen.blit(frame, (0, 0))
            pygame.display.update()

            time.sleep(1 / FPS)

        # Call it always before finishing. To deallocate resources.
        
        self.tello.end()

    def keydown(self, key):
        """ Update velocities based on key pressed
        Arguments:
            key: pygame key
        """
        if key == pygame.K_UP:  # set forward velocity
            self.for_back_velocity = S
        elif key == pygame.K_DOWN:  # set backward velocity
            self.for_back_velocity = -S
        elif key == pygame.K_LEFT:  # set left velocity
            self.left_right_velocity = -S
        elif key == pygame.K_RIGHT:  # set right velocity
            self.left_right_velocity = S
        elif key == pygame.K_w:  # set up velocity
            self.up_down_velocity = S
        elif key == pygame.K_s:  # set down velocity
            self.up_down_velocity = -S
        elif key == pygame.K_a:  # set yaw counter clockwise velocity
            self.yaw_velocity = -S
        elif key == pygame.K_d:  # set yaw clockwise velocity
            self.yaw_velocity = S

    def keyup(self, key):
        """ Update velocities based on key released
        Arguments:
            key: pygame key
        """
        if key == pygame.K_UP or key == pygame.K_DOWN:  # set zero forward/backward velocity
            self.for_back_velocity = 0
        elif key == pygame.K_LEFT or key == pygame.K_RIGHT:  # set zero left/right velocity
            self.left_right_velocity = 0
        elif key == pygame.K_w or key == pygame.K_s:  # set zero up/down velocity
            self.up_down_velocity = 0
        elif key == pygame.K_a or key == pygame.K_d:  # set zero yaw velocity
            self.yaw_velocity = 0
        elif key == pygame.K_t:  # takeoff
            self.tello.takeoff()
            self.send_rc_control = True
        elif key == pygame.K_l:  # land
            self.tello.land()
            self.send_rc_control = False

    def update(self):
        """ Update routine. Send velocities to Tello."""
        if self.send_rc_control:
            self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity, self.up_down_velocity,
                                       self.yaw_velocity)

class AutonomousDrone(object):
    """ Contains the tello autonomous flight modes.
        
    """

    def __init__(self, args):
        # Parse arguements
        self.move_mode = args.move_mode 
        self.display_stream = args.display_stream 
        self.dryrun = args.dryrun
        self.save_stream =args.save_stream
        self.save_meta=args.save_meta
        self.ops_mode = args.ops_mode
        self.log_level = args.log_level
        self.path_to_data =  '/home/pi/data/'
        self.path_to_routecsv =  '/home/pi/dronelab/routes/route_test.csv' # make configurable
        self.fname_meta_global = 'meta_global.csv' # filename for global metadata
        self.df_meta_global = []#pd.DataFrame(columns=['run_begin', 'serial_number', 'move_mode','route','battery_initial','temperature_initial','sec_in_air_max','FPS', 'flight_start_time' ])
        self.fname_meta_run ='meta_run.csv'# filename for temporal metadata for run
        self.df_meta_run = [] #pd.DataFrame(columns=['elapsed_time', 'frame', 'battery','temperature','flight_time','height','attitude','get_distance_tof','get_barometer'])
      
        self.frames_to_save = {}
    
        self.path_to_log = '/var/log/dronelab'
        self.props_fly = args.props_fly
        self.prop_to_save = {}
        self.FPS = 10

        # internal 
        self.send_rc_control = False

       
    def setup_logger(self): 
        module = sys.modules['__main__'].__file__
        logfile = self.path_to_log+'/runDrone.log'
        logging.basicConfig(filename=logfile,format='%(asctime)s-%(process)d-%(name)s-%(levelname)s- %(message)s',level=logging.DEBUG)
        logger = logging.getLogger(module)

        self.logger = logger
        

    def configure(self):

        self.setup_logger()
        self.logger.setLevel(self.log_level)    


        self.is_conf_success = True
         # COnfigure:   cheh serial nr, chech battery status
        self.run_begin = datetime.now()
        self.run_begin_str = self.run_begin.strftime("%Y-%m-%d-%H-%M-%S")
    
        if not "DISPLAY" in os.environ:
            self.logger.debug("DISPLAY not set in environment")
            self.logger.debug("Setting Display  to :0.0")
            os.environ["DISPLAY"]=":0.0"
 
        ##check for Wifi of Tello, if no existant exit, else connect
        self.tello_name = "TELLO-588A0C" # Wifi to which tello will connect
        self.serial_number = self.tello_name # serial_number for unique id of device, for tello drones take this
        
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
        self.tello = TelloNew()

        try:
            self.tello.connect()
        except Exception as e:
            self.logger.info("Tello not connected,  closing  attempt to run... reason: "+str(e))
            self.is_conf_success = False
            return    

        self.battery_initial =  self.tello.get_battery()

        self.logger.debug("battery_initial "+ str(self.battery_initial))

        self.temperature_initial = self.tello.get_temperature()


        try:
            self.temperature_initial = int(self.temperature_initial.split('~')[0])
        except:
            0
        self.logger.debug("temperature_initial"+ str(self.temperature_initial))

        if self.temperature_initial > 93:    
            self.logger.debug("Temperature to high > 93 stop configuring and exit....") 
            return
 

        if self.save_stream or self.save_meta:
            self.save_stream_to = os.path.join(self.path_to_data,self.serial_number,self.run_begin_str)
            if not os.path.exists(self.save_stream_to):
                os.mkdir(self.save_stream_to)


        if self.display_stream:
        # Init pygame
            pygame.init()

            # Creat pygame window
            pygame.display.set_caption("Tello video stream")
            self.screen = pygame.display.set_mode([960, 720])
            pygame.time.set_timer(pygame.USEREVENT + 1, 50)
         

        if self.move_mode == 'fixroute': #initialise route
            self.load_route()   

     
        self.sec_in_air_max = 10 ## Seconds in air after first frame of stream before going down (in startland mode)
        if self.move_mode == 'fixroute':
            self.sec_in_air_max = self.route['sec'].sum() + 2 ## 5 seconds startup time .. voluimnous guess

      
        # Drone velocities between -100~100
        self.logger.info("Set speed to 0")
        self.set_vel_to0()

         

    def load_route(self):
        self.route = pd.read_csv(self.path_to_routecsv)
        #self.route['sec'].shift(1)
        

        self.route['sec_cum'] = self.route['sec'].shift(1).cumsum()
        self.route['sec_cum'].iloc[0]=0
        self.route['updated'] = False
        ## include sanity check if sec_cum is not in columns twice  ## lowest resolution is seconds
        self.logger.info(self.route)
            
    
    def set_vel_to0(self):
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10    

    def fps_waiter(self,elapsed_time):
        time.sleep(1 / self.FPS) ## very coarse estimate time to wait by FPS -> get better calcualtion based on elapsed_time....    

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

        frame_read = self.tello.get_frame_read()

        should_stop = False
        self.logger.info("Will fly in mode "+ self.move_mode+ "for seconds: "+ str(self.sec_in_air_max))
                
        if self.dryrun:
            self.logger.info("Dryrun-- Would fly in "+ self.move_mode+ "for seconds: "+ str(self.sec_in_air_max))
            self.tello.end()
            pygame.display.quit()
            return 
           
        # Her beginn with frone flying  # use flight_time to sendnew commands in fixroute
        try:
            self.tello.takeoff()
        except Exception as Error:
            self.logger.error(Error)
            return
        #time.sleep(2)    
        self.send_rc_control = True
        self.update()
        
        start_time = time.time() # 

        if self.save_meta:
            self.df_meta_global.append({'run_begin':self.run_begin_str, 
                                                'serial_number':self.serial_number, 
                                                'move_mode':self.move_mode,
                                                'route':self.path_to_routecsv,
                                                'battery_initial':self.battery_initial,
                                                'temperature_initial':self.temperature_initial,
                                                'sec_in_air_max':self.sec_in_air_max,
                                                'FPS':self.FPS,
                                                'flight_start_time':start_time}) 
        entered_save_mode = False    
        i_frame = 0
        while not should_stop:

            elapsed_time = time.time() - start_time      
            if self.move_mode == 'fixroute':
                do_update_rc = self.set_state_fixroute(elapsed_time)
                self.logger.debug("fixroute do_update_rc"+ str(do_update_rc)+" elapsed time"+ str(elapsed_time))
                if do_update_rc:
                    self.update()     

            i_frame +=1           
            if frame_read.stopped:
                frame_read.stop()
                break

            frame_cv = cv2.cvtColor(frame_read.frame, cv2.COLOR_BGR2RGB) # RGB_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            frame_cv_save = frame_cv.copy()
            frame_cv = np.rot90(frame_cv)
            frame_cv = np.flipud(frame_cv)

            
            if self.display_stream:        
                self.screen.fill([0, 0, 0])
                frame = pygame.surfarray.make_surface(frame_cv)
                self.screen.blit(frame, (0, 0))
                pygame.display.update()

            if self.save_stream:
               filename = "fps_"+str(self.FPS)+"_frame_"+str(i_frame)+".jpg"
               
               if np.sum(frame_cv_save) !=0:

                   
                    self.frames_to_save[filename] = frame_cv_save

                
           

            if self.save_meta:
                #states = self.tello.get_states()
                self.df_meta_run.append({'elapsed_time':elapsed_time, 
                                                'frame':i_frame,
                                                'timestamp': str(datetime.now().strftime("%H:%M:%S")), 
                                                'battery':self.tello.get_battery(),
                                                'temperature':self.tello.get_highest_temperature(),
                                                'flight_time':self.tello.get_highest_temperature(),
                                                'height':self.tello.get_height(),
                                                'pitch':self.tello.get_pitch(),
                                                'roll':self.tello.get_roll(),
                                                'yaw':self.tello.get_yaw(),
                                                'get_distance_tof':self.tello.get_distance_tof(),
                                                'get_barometer':self.tello.get_barometer})
                                                
               
            
           
            self.logger.info("elapsed_time since first frame "+str(elapsed_time)+" "+str(i_frame))
            
            self.fps_waiter(elapsed_time)     ## to be implemented       
                      
            if elapsed_time > self.sec_in_air_max:
                self.logger.info("Time is up.. initiating landing after second: "+str(elapsed_time))
                should_stop = True

        try:
            self.tello.land()
        except:
            self.logger.info("landing failed..trying to save stream")
        
        self.logger.info("Time to save stream after seconds: "+str(elapsed_time))
        self.logger.info("Saving stream to "+self.save_stream_to)
          
        if self.save_meta:
            pd.DataFrame(self.df_meta_run).to_csv(os.path.join(self.save_stream_to, self.fname_meta_run))
            pd.DataFrame(self.df_meta_global).to_csv(os.path.join(self.save_stream_to, self.fname_meta_global))
            copyfile(self.path_to_routecsv,os.path.join(self.save_stream_to,"route.csv")) 
        if self.save_stream:
                     for f,img in self.frames_to_save.items():
                         cv2.imwrite(os.path.join(self.save_stream_to,f ) ,img)
        self.logger.info("Saving of stream and metadaa finished")
                        


        #res = self.F.protect_gateway_interface()
        #self.logger.info("Protecting against wlan gatewy interface switch:", res)
        if self.ops_mode:
            self.logger.info('Wating for 2 Minutes to prevent another run within the next minute... Tello Drone will switch itselt off within 15 minutes.')
            time.sleep(2*60)
        
        # Call it always before finishing. To deallocate resources.
        self.tello.end()
        pygame.display.quit()


        
    def update(self):
        """ Update routine. Send velocities to Tello."""
        if self.send_rc_control:
            self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity, self.up_down_velocity,
                                       self.yaw_velocity)

    def set_state_fixroute(self,elapsed_time):
        ## replace this with a generator
        do_update = False

        sec_cum = self.route['sec_cum'].values
       

        if int(elapsed_time) in  sec_cum:  ## why is 0 in here?
            row = self.route.loc[self.route['sec_cum'] == int(elapsed_time)]
            #self.logger.debug(row)
            was_updated = row['updated'].values[0]   
            if was_updated:
                do_update = False
            else:
                self.left_right_velocity = int(row['left_right_velocity'].values[0])
                self.for_back_velocity = int(row['for_back_velocity'].values[0] ) 
                self.up_down_velocity = int(row['up_down_velocity'].values[0])  
                self.yaw_velocity   = int(row['yaw_velocity'].values[0] ) 

                row['updated']  = True
                self.route.loc[self.route['sec_cum'] == int(elapsed_time)] = row
                do_update = True
        else: 
            do_update = False

        return do_update

def just_connect():
    tello = TelloNew()
    try:
            tello.connect()
    except Exception as e:
            #self.logger.debug("Tello not connected, please check the following: Turn on Tello Drone, Connect to Tello Wifi. Error:",e)
            0
            return

    battery_full = 100

    start_time = time.time()
    tello.set_speed(10)
   
    while battery_full> 5:
        battery_status =  tello.get_battery()
        flight_time =   tello.get_flight_time()
        height =   tello.get_height()
        temp =   tello.get_temperature()
        
        elapsed_time = time.time() - start_time
        #self.logger.debug("elapsed_time", elapsed_time)
        #self.logger.debug("flight_time", flight_time)
        #self.logger.debug("battery_status", battery_status)
        #self.logger.debug("height",height)
        #self.logger.debug("temp",temp)
        time.sleep(1)


def loadarguments():
    parser = argparse.ArgumentParser(description='Options for Drone Runner')

    parser.add_argument('--dryrun', dest='dryrun', action='store_true',
                        default=False,
                        help='Do a dryrun.. configure everything but then only show what would have been executed')
    parser.add_argument('--move_mode', dest='move_mode', choices=["noflight","byhuman","startland","fixroute","adaptive"],
                        default=False,
                        help='Select mode, one of the following:""noflight": just switch on drone, "byhuman": steer drone via laptop and keys, "startland": Only Start and Land, "fixroute": a fixed route, "adaptive": adaptive route to task goal ')
    parser.add_argument('--save_stream', dest='save_stream', action='store_true',
                        default=False,
                        help='Save stream (tbd: and register to database)')
    parser.add_argument('--save_meta', dest='save_meta', action='store_true',
                        default=False,
                        help='Save meta data (tbd: and register to database)')                    
    parser.add_argument('--ops_mode', dest='ops_mode', action='store_true',
                        default=False,
                        help='Operating mode in Lab for deployment')
    parser.add_argument('--display_stream', dest='display_stream', type=bool,
                        default=False,
                        help='Camerastream to be displayed on screen')
    parser.add_argument('--props_fly', dest='props_fly', type=bool,
                        default=False,
                        help='Evaluate properties on the fly and add to screen')                    
    parser.add_argument('--log_level', dest='log_level', type=str,
                        default='INFO',
                        choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'],
                        help='Log Level')                                       

    args = parser.parse_args()
    return args



def main(args):
    
    
    # run frontend
    if args.move_mode == "byhuman":
        frontend = FrontEnd()    
        frontend.run()
    elif args.move_mode in ["startland","fixroute"]:
        print('starting in mode ', args.move_mode, args.dryrun)
        autodrone = AutonomousDrone(args)
         # setup logger
         
        autodrone.configure()
        if autodrone.is_conf_success:

            autodrone.run()
        else:
            autodrone.logger.info("Skipping run, since is_conf_success = False")
    elif args.move_mode == "noflight":
        just_connect()
    else:
        0
        






if __name__ == '__main__':

    

      # interpret arguments
    args = loadarguments()

    print(args)
    
    #logging.info(args)

    main(args)
