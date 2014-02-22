from errbot import BotPlugin, botcmd
import subprocess,os

class Hello(BotPlugin):
    """Example 'Hello, world!' plugin for Err"""

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
        arg='/home/pi/usr/src/Python/utils/cam.py'
        p=subprocess.Popen(arg,shell=True,stdout=subprocess.PIPE)
        arg='/home/pi/usr/src/Python/utils/mail.py %s'%quien
        p=subprocess.Popen(arg,shell=True,stdout=subprocess.PIPE)
        my_msg = 'Mando la foto ... %s'%quien
        yield "Thanks for sending this command**"
        yield my_msg

