from errbot import BotPlugin, botcmd
import subprocess,os,time

import cv2, time

import smtplib, mimetypes, time
from email import Encoders
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart


class Pruebas(BotPlugin):
    """Example 'Hello, world!' plugin for Err"""

    def get_configuration_template(self):
        return{'ADDRESS' : u'kk@kk.com', 'FROMADD' : u'kk@kk.com', 'TOADDRS' : u'kk@kk.com', 'SUBJECT' : u'Imagen', u'SMTPSRV' : u'smtp.gmail.com:587', 'LOGINID' : u'changeme', 'LOGINPW' : u'changeme'} 

    @botcmd
    def hello(self, msg, args):
        """Say hello to the world"""
        yield "Hello, %s!"%msg.getFrom().getStripped()
        yield "Hello, %s!"%msg.getTo()
        yield "Hello, world!"

    @botcmd
    def ip(self, msg, args):
        """Say my internal ip"""
        arg='ip route list'
        p=subprocess.Popen(arg,shell=True,stdout=subprocess.PIPE)
        data = p.communicate()
        split_data = data[0].split()
        ipaddr = split_data[split_data.index('src')+1]
        my_ip = 'La ip de la raspberry es %s' %  ipaddr
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
        quien=msg.getFrom().getStripped()
        yield "I'm taking the picture, wait a second "
        if (args):
            try:
               cam=int(args)
            except:
               cam=0
        else:
	    cam=0
        yield "Camera %s"%cam
        self.camera("/tmp/imagen.png",cam)
        yield "Now I'm sending it"
        self.mail("/tmp/imagen.png", quien)
        my_msg = "I've sent it to ... %s"%quien
        yield my_msg

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
        adjunto = MIMEBase(main, sub)
        adjunto.set_payload(open(imgFile,"rb").read())
        Encoders.encode_base64(adjunto)
        adjunto.add_header('Content-Disposition', 'attachment; filename="%s"' % imgFile)
        mensaje.attach(adjunto)


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
