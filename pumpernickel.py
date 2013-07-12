#!/usr/bin/env python3
import sys
import os

from PyPump.PyPump import PyPump
import webbrowser



class Pumpernickel():
    def __init__(self,args):
        self.client_name = 'Pumpernickel'

        self.user = None
        self.oauth_token = None
        self.oauth_token_secret = None
        self.oauth_client_id = None
        self.oauth_client_secret = None
        self.configFile = None
        self.config = None
        
        if not self.checkConfigFile():
            self.doSetup()

        

    def checkConfigFile(self):
        self.configFile = os.path.join(os.environ['HOME'],'.config',self.client_name.lower())
        if not os.path.exists(self.configFile):
            os.makedirs(self.configFile)
        self.configFile = os.path.join(self.configFile,self.client_name.lower() + '.conf')

        if not os.path.exists(self.configFile):
            print('config file is invalid: ' + self.configFile)
            return False

        print('config file check is done')
        print('config file: ' + self.configFile)
        return True

    def doSetup(self):
        self.webfinger = input('Enter your webfinger ID (ie. "jrobb@microca.st", no quotes):')
        if '@' not in self.user:
            print('not a valid webfinger address')
            return False

        self.user, self.server = self.webfinger.split('@')

        self.pump = PyPump(self.webfinger, client_name=self.client_name)
        
        registration = self.pump.get_registration()  #return (self.consumer.key, self.consumer.secret, self.consumer.expirey)
        self.oauth_client_id = registration[0]
        self.oauth_client_secret = registration[1]
        self.oauth_client_expirey = registration[2]
        del registration
        
        token = self.pump.get_token() #return (self.token, self.token_secret)
        self.oauth_token = token[0]
        self.oauth_token_secret = token[1]
        del token

        print('setup stuff done, write to config file:')
        self.writeConfig()

    def writeConfig(self):            
        with open(self.configFile, 'w') as f:
            f.write('webfinger,' + self.webfinger)
            f.write('\n')
            f.write('oauth_client_id,' + self.oauth_client_id )
            f.write('\n')
            f.write('oauth_client_secret,' + self.oauth_client_secret)
            f.write('\n')
            f.write('oauth_token,' + self.oauth_token)
            f.write('\n')
            f.write('oauth_token_secret,' + self.oauth_token_secret)
            f.write('\n')

            f.close()
        
    def readConfig(self):
        print('reading config file')
        with open(self.configFile, 'r') as f:
            self.config = f.readlines() #read the lines into a list
            f.close()

        print('checking the data if it exists:')
        if self.config:
            for line in self.config:
                lineVars = line.split(',')
                print(lineVars[0] + ' :: ' + lineVars[1])
                if 'webfinger' in line and self.user == None:
                    self.user, self.server = lineVars[1].split("@")
                elif 'oauth_client_id' in line:
                    self.oauth_client_id =  lineVars[1]
                elif 'oauth_client_secret' in line:
                    self.oauth_client_secret = lineVars[1]
                elif 'oauth_token_secret' in line:
                    self.oauth_token_secret = lineVars[1]
                elif 'oauth_token' in line:
                    self.oauth_token = lineVars[1]
                else:
                    print('unknown config param: ' + line)

            if not self.user or not self.server or not self.oauth_token_secret or not self.oauth_client_secret:
                print('user info not sufficiently filled out!')
                if not self.user:
                    print('user')
                elif not self.server:
                    print('server')
                elif not self.oauth_token_secret:
                    print('token secret')
                elif not self.oauth_client_secret:
                    print('client secret')
                    
                sys.exit()
                
            self.webfinger = self.user + '@' + self.server
            print('webfinger: ' + self.webfinger)
            
            isSecure = True #default to https

            #~ (self, server, key=None, secret=None, 
                #~ client_name="", client_type="web", token=None, 
                #~ token_secret=None, save_token=None, secure = True):
            self.pump = PyPump( \
                server=self.server, \
                key=self.oauth_client_id, \
                secret=self.oauth_client_secret, \
                client_name=self.client_name, \
                client_type="native",   \
                token=self.oauth_token, \
                token_secret=self.oauth_token_secret, \
                secure= isSecure \
                )

            
        else:
            print('no information, do setup')
            self.doSetup()

        self.pump.set_nickname(self.user.split('@')[0])

        print('done reading config file.  loaded.')

    def run(self):
        print('running')
        self.readConfig()
        print('startup is finished')


    #~ pump.set_nickname('jrobb')
    #~ print('nickname was set')
#~ 
    #~ print('attempting to post note:')
    #pump.post_note("one last test post (from python), using this libstuff: https://github.com/xray7224/PyPump ")
    #~ if postContent != '':
        #~ pump.post_note(postContent)    
        #~ print('note posted')

    #print('here\'s the inbox:')
    #print(pump.inbox('major'))
    #~ print('...done...')

if __name__ == "__main__":
    app = Pumpernickel(sys.argv[1:])
    app.run()
