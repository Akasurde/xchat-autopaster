"""
This module for Xchat has been written by Stephen "TheCodeAssassin" Hoogendijk.

Modified By:
Sanket Jagtap
Abhijeet Kasurde
Bhavik Bhavsar

It's largely inspired by (now defunct) module copypastebin plugin

"""

__module_name__ = "Xchat-Autopaster"
__module_version__ = "1.0.1"
__module_description__ = "A script that automatically pastes multiline text and returns a URL."

#Telling the user we loaded the plugin
print "\0034", __module_name__, __module_version__, "has been loaded :) \003"


#Importing necessary modules
import xchat
import json
import shelve
import random
import requests

#Load persistent config file
settings = shelve.open("copypastegist.conf", writeback=True)

#Setting default values if first time launching
if not settings.has_key("timeout"):
    settings['timeout'] = 50
if not settings.has_key("limit"):
    settings['limit'] = 3

#Init the message buffer
list_ = None

#The default command, used whenever you type something in the textfield
def say_cb(word, word_eol, userdata):
    global list_

    #If the list exists, we append the current message to it, if not we create a new list and set a timer.
    if list_:
        list_.append(word_eol[0])
    else:
        #Create the list and set a timer when the list should be dealt with
        list_ = []
        list_.append(word_eol[0])
        xchat.hook_timer(settings['timeout'], messagebuffer, )
    return xchat.EAT_ALL

#The decision taker, decides what to do with the list.
def messagebuffer(dunno):
    global list_

    #Makes sure we have locked the list so that we start on a new list if we send messages during execution
    tmplist = list_
    list_ = None

    #Get's the current channel, so we know where we should send messages
    channel = xchat.get_info('channel')

    #If the list is shorter than the pastelimit, just send them one by one to the irc-server
    if len(tmplist) <= settings['limit']:
        for i in tmplist:
            #send the actual string
            xchat.command("PRIVMSG %s :%s" % (channel, i))

            #recreate the output from a regular message, as this is just a regular message
            xchat.emit_print("Your Message", xchat.get_info('nick'), i, "@")
    else:
        #Add all the lines together into a string
        str_ = ""
        for i in tmplist:
            str_ += i + "\n"

        # do the paste
        pastie_url = do_pastie(str_[:-1])

        xchat.command("PRIVMSG %s :%s" % (xchat.get_info('channel'), pastie_url))
        xchat.emit_print("Your Message", xchat.get_info('nick'), pastie_url, "@")

        return 0  # Return 0 so we don't repeat the timer.

# returns URL
def do_pastie(contents):
    url = 'http://paste.example.com/pastebin.php'

    c = {}
    c['email'] = 1
    c['paste'] = 1
    c['remember'] = 1
    c['poster'] = xchat.get_info('nick')
    # Uncomment for Python format
    # c['format'] = 'python'
    c['expiry'] = 'm'
    c['code2'] = contents

    response = requests.post(url, data=c)
    pastie_url = response.url

    return pastie_url

#Handle variables. (NOT A NICE METHOD, NEEDS REWRITE)
def pastevar_cb(word, word_eol, userdata):
    global settings
    #Check amount of arguments
    if len(word) == 1:
        #If no arguments, print list of variables and what they do.
        xchat.prnt(
            "timeout: amount of time to wait for new messages. If your paste splits up in several messages you could try to increase this. (default 50 MS)")
        xchat.prnt("limit: Amount of messages maximum to print in chat before pastebin kicks in. (default 3)")

    elif len(word) == 2:
        #If one argument, print the value of the variable
        if word[1].lower() == "timeout":
            xchat.prnt("timeout: " + str(settings['timeout']) + " MS")

        elif word[1].lower() == "limit":
            xchat.prnt("limit: " + str(settings['limit']))

        else:
            #If it was an invalid variable, print that
            xchat.prnt("Unknown variable " + word[1])

    elif len(word) == 3:

        #If we have 2 arguments, set the value. Print an error message if we received invalid input
        if word[1].lower() == "timeout":
            try:
                settings['timeout'] = int(word[2])
                xchat.prnt("timeout set to " + str(settings['timeout']) + " MS")

            except:
                xchat.prnt("please enter a numerical value only")

        elif word[1].lower() == "limit":
            try:
                settings['limit'] = int(word[2])
                xchat.prnt("limit set to " + str(settings['limit']))

            except:
                xchat.prnt("please enter a numerical value only")

        else:
            #If it was an invalid variable, print that
            xchat.prnt("Unknown variable " + word[1])
        settings.sync()

    else:
        #If we have more than 2 arguments, print syntaxerror.
        xchat.prnt(
            "USAGE: PASTEVAR [variable] [value] checks or sets a variable in the copypastebin plugin. No arguments list available variables.")

    #return EAT_ALL so xchat doesn't start parsing this and send doubles.
    return xchat.EAT_ALL

#Close the settingsfile on unload
def unload_cb(userdata):
    settings.close()

#Register the hooks
xchat.hook_unload(unload_cb)
xchat.hook_command("", say_cb)
xchat.hook_command("PASTEVAR", pastevar_cb, help="PASTEVAR [variable] [value] checks or sets a variable in the copypastegist plugin. No arguments list available variables.")

