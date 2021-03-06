
import logging
import sleekxmpp

from config import minT,maxT
import access_codes

from Thermostat import Mode

class ThermoBot(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, thermostat):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.thermostat = thermostat
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)

    def start(self, event):
        logging.info("chat bot got start event")
        self.send_presence()
        self.get_roster()

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            if msg['from'].user in access_codes.xmpp_auth_accounts:
                setTemp = self.thermostat.getSetTemp()
                temp = self.thermostat.getTemp()
                mode = self.thermostat.getMode()
                body = msg['body'].lower()
                if body == "?":
                    if mode == Mode.On:
                        msg.reply("Heat is ON.  Current temp is %.1f" % temp).send()
                    elif mode == Mode.Off:
                        msg.reply("Heat is OFF.  Current temp is %.1f" % temp).send()
                    elif mode == Mode.Thermostat:
                        msg.reply("Thermostat is set to %.0f.  Current temp is %.1f" % (setTemp, temp)).send()
                    else:
                        msg.reply("I know you're smarter than this").send()
                elif body == 'on':
                    self.thermostat.setMode(Mode.On)
                    msg.reply("Heat is ON.  Current temp is %.1f" % temp).send()
                elif body == 'off':
                    self.thermostat.setMode(Mode.Off)
                    msg.reply("Heat is OFF.  Current temp is %.1f" % temp).send()
                elif body.startswith('set '):
                    try:
                        newSetTemp = float(body[4:])
                        if newSetTemp < minT:
                            msg.reply("%.0f seems awful cold" % newSetTemp).send()
                        elif newSetTemp > maxT:
                            msg.reply("%.0f seems awful hot" % newSetTemp).send()
                        else:
                            self.thermostat.setSetTemp(newSetTemp)
                            self.thermostat.setMode(Mode.Thermostat)
                            msg.reply("Thermostat is set to %.0f.  Current temp is %.1f" % (newSetTemp, temp)).send()
                    except Exception as e:
                        msg.reply("I can't set the thermostat to '%s'" % body[4:]).send()
                else:
                    msg.reply("I don't know what '%s' means." % body).send()
            else:
                    msg.reply("Not sure I can trust you, %s." % msg['from'].user).send()

