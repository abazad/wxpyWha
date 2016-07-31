#!/usr/bin/python
# -*- coding: utf-8 -*-

"""@package docstring
Yowsup connector for wxpyWha (a simple wxWidgets GUI wrapper atop yowsup).

Defines custom YowInterfaceLayer called WhaLayer.

This is based on code from the yowsup echo example, the yowsup cli and pywhatsapp.
"""

# from echo stack
from yowsup.layers.network import YowNetworkLayer

# from echo layer
from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback

# from cli layer
from yowsup.layers import EventCallback

import sys

class WhaLayerInterface():
    """Interface class for connecting the layer object with the GUI."""
    def __init__(self):
        self.enventHandler = None
        self.sendMessage = None

class WhaLayer(YowInterfaceLayer):
    """Custom YowInterfaceLayer class for wxpyWha."""
    def __init__(self):
        super(WhaLayer, self).__init__()
        YowInterfaceLayer.__init__(self)
        self.interface = WhaLayerInterface() # TODO: I have no idea if this is the correct way of using the interface attribute
        self.interface.sendMessage = self.sendMessage # TODO: I have no idea if this can be called in out-of-thread context
        self.connected = False
    
    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):
        sys.stderr.write("Received a message from %s of type %s\n"%(messageProtocolEntity.getFrom(),messageProtocolEntity.getType()))
         # taken from yowsup cli
         # sends ack to server AND marks message as read (upon repeated receival axolotl will do so anyways)
        self.toLower(messageProtocolEntity.ack(True))
        if self.interface.enventHandler:
            self.interface.enventHandler.handleEvent(messageProtocolEntity)

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        sys.stderr.write("Received a receipt with ID %s, sending ack.\n"%(entity.getId()))
        self.toLower(entity.ack())
        
    @ProtocolEntityCallback("ack")
    def onAck(self, entity):
        """This indicates that the WhatsApp server received our message."""
        #sys.stderr.write("Received an acknowledgement with ID %s.\n"%(entity.getId()))
        if self.interface.enventHandler:
            self.interface.enventHandler.handleEvent(("ack",entity))

    @EventCallback(YowNetworkLayer.EVENT_STATE_DISCONNECTED)
    def onStateDisconnected(self,layerEvent):
        self.connected = False
        sys.stderr.write("Disconnected. Reason: %s\n" % layerEvent.getArg("reason"))
        
    @ProtocolEntityCallback("success")
    def onSuccess(self, entity):
        self.connected = True
        sys.stderr.write("Success: Logged in.\n")

    @ProtocolEntityCallback("failure")
    def onFailure(self, entity):
        sys.stderr.write("Login Failed. Reason: %s\n" % entity.getReason())
        
    def sendMessage(self, outgoingMessage):
        #sys.stderr.write("WhaLayer.sendMessage. MessageID is %s\n"%(outgoingMessage.getId()))
        if not self.connected:
            sys.stderr.write("Cannot send message. Not connected.\n")
            if self.interface.enventHandler:
                self.interface.enventHandler.handleEvent(("sendMessage",outgoingMessage,"Cannot send message. Not connected."))
        else:
            self.toLower(outgoingMessage)
            if self.interface.enventHandler:
                self.interface.enventHandler.handleEvent(("sendMessage",outgoingMessage,True))
            

