
# msg.getFrom().getStripped() has disappeared
# I've replaced it with msg.frm.person
from errbot import BotPlugin, botcmd

import subprocess,os,time
import math
from RPIO import PWM

MAX=2340
MIN=600
VEL=0.4

import cv2, time

import smtplib, mimetypes, time, datetime
from email import Encoders
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart


class Camera(BotPlugin):
    """Example 'Hello, world!' plugin for Err"""
    cam=0
    posCam=90
    servoGPIO=4


    def get_configuration_template(self):
        self.movePos(self.posCam)
        return{'ADDRESS' : u'kk@kk.com', 'FROMADD' : u'kk@kk.com', 'TOADDRS' : u'kk@kk.com', 'SUBJECT' : u'Imagen', u'SMTPSRV' : u'smtp.gmail.com:587', 'LOGINID' : u'changeme', 'LOGINPW' : u'changeme'} 

    @botcmd
    def hello(self, msg, args):
        """Say hello to the world"""
        #yield "Hello, %s!"%msg.getFrom().getStripped()
        yield "Hello, %s!"%msg.frm.person
        yield "Hello, %s!"%msg.getTo()
        yield "Hello, world!"

    @botcmd
    def tellpos(self, msg, args):
        """Say my internal ip"""
        yield self.posCam

    @botcmd
    def ip(self, msg, args):
        """Say my internal ip"""
        arg='ip route list'
        p=subprocess.Popen(arg,shell=True,stdout=subprocess.PIPE)
        data = p.communicate()
        split_data = data[0].split()
        ipaddr = split_data[split_data.index('src')+1]
        my_ip = 'La ip de la raspberry es %s' % ipaddr
        #yield "Thanks for sending\n**%(body)s**" % msg
        yield my_ip

    @botcmd
    def ls(self, msg, args):
        """List current dir"""
        lista=os.listdir('.')
        for filename in lista:
            yield "> %s "%filename
 
    @botcmd
    def foto(self, msg, args):
        """Take a picture"""
        quien=msg.frm.person
        yield "I'm taking the picture, wait a second "
        if (args):
            try:
                cam=int(args)
            except:
                cam=0
        else:
            cam=0
        yield "Camera %s"%cam
        self.camera("/tmp/imagen.png",self.cam)
        yield "Now I'm sending it"
        self.mail("/tmp/imagen.png", quien)
        my_msg = "I've sent it to ... %s"%quien
        yield my_msg

    # This function maps the angle we want to move the servo to, to the needed
    # PWM value
    #
    # https://github.com/MattStultz/PiCam
    #
    def angleMap(self, angle):
        return int((round((1950.0/180.0),0)*angle)/10)*10+550

    def movePos(self, pos):
        servo = PWM.Servo()
        print pos 
        print self.posCam 
        servo.set_servo(self.servoGPIO, self.angleMap(pos))
        time.sleep(VEL)
        servo.stop_servo(self.servoGPIO)
        self.posCam=pos

    def move(self, pos, inc=1):
        if (pos < self.posCam):
            inc = -1*inc
        for i in range(self.posCam, pos, inc):
            self.movePos(i)


    def camera(self, imgFile, whichCam):
        """Take a picture"""
        cam=cv2.VideoCapture(whichCam)
        cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 1280)
        cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 960)
        retval, img = cam.read() 
        cv2.imwrite(imgFile, img)
        del(cam)

    def mail(self, imgFile, address=""):
        """Send a file by mail"""

        destaddr = self.config['ADDRESS']
        fromaddr = self.config['FROMADD']
        if (address==""):
            toaddrs=self.config['TOADDRS']
        else:
            toaddrs  = address
            subject  = self.config['SUBJECT']
            smtpsrv  = self.config['SMTPSRV']
            loginId  = self.config['LOGINID']
            loginPw  = self.config['LOGINPW']
    
            mensaje = MIMEMultipart()
    
            format, enc = mimetypes.guess_type(imgFile)
            main, sub = format.split('/')
            text = "Picture taken on: %s"%datetime.datetime.now().isoformat()
            # We are including the date in the body of the message.
            part1 = MIMEText(text, 'plain')

            part2 = MIMEBase(main, sub)
            part2.set_payload(open(imgFile,"rb").read())
            Encoders.encode_base64(part2)
            part2.add_header('Content-Disposition', 'attachment; filename="%s"' % imgFile)
            mensaje.attach(part1)
            mensaje.attach(part2)
    
    
            mensaje['Subject'] = subject
            mensaje['From'] = fromaddr
            mensaje['To'] = destaddr
            mensaje['Cc'] = toaddrs
    
            server = smtplib.SMTP()
            #server.set_debuglevel(1)
            server.connect(smtpsrv)
            server.ehlo()
            server.starttls()
            server.login(loginId, loginPw)
            server.sendmail(fromaddr, [destaddr]+[toaddrs], mensaje.as_string(0))
            server.quit() 

    @botcmd
    def rfoto(self, msg, args):
        #Move the servo, take the picture, send it.
        #It won't return to the initial position

        if (args):
            try:
                mov = int(args)
            except:
                mov = 90
        else:
            mov = 90

        yield "Going to %d"%mov
        self.movePos(mov)

        quien=msg.frm.person

        yield "I'm taking the picture, wait a second "
        self.camera("/tmp/imagen.png",self.cam)

        yield "Now I'm sending the picture"
        self.mail("/tmp/imagen.png", quien)

        my_msg = "I've sent it to ... %s"%quien

    @botcmd
    def mfoto(self, msg, args):
        # Move the servo, take the picture, send it, return to
        # the initial position. Now with angles instead percentages."""

        if (args):
            try:
                mov = int(args)
            except:
                mov = 90
        else:
            mov = 90

        yield "Going to %d"%mov
        self.move(mov)
        yield "In %d"%mov

        quien=msg.frm.person

        yield "I'm taking the picture, wait a second "
        self.camera("/tmp/imagen.png",self.cam)

        yield "Now I'm sending the picture"
        self.mail("/tmp/imagen.png", quien)

        my_msg = "I've sent it to ... %s"%quien



