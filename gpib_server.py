#!/usr/bin/python3

import zmq
import time
import sys
import random
from PowerSupplyControls import getPowerSupply, SiglentSPD1168X
import logging

logging.basicConfig(filename='server_log.log', level=logging.INFO, format="[%(asctime)s] %(levelname)-2s: %(name)-15s %(message)s")
logger = logging.getLogger("gpib_server")


powerSupplies={}
for addr in ['42','43','44','46','48']:
    try:
        powerSupplies[addr] = getPowerSupply('192.168.1.50',addr[-1])
        logger.info(f'Found power supply {addr} on gpib with ip 192.168.1.50')
    except:
        try:
            powerSupplies[addr] = getPowerSupply('192.168.1.51',addr[-1])
            logger.info(f'Found power supply {addr} on gpib with ip 192.168.1.51')
        except:
            try:
                powerSupplies[addr] = SiglentSPD1168X(f'192.168.1.1{addr}')
                logger.info(f'Found power supply {addr} on gpib with ip 192.168.1.1{addr}')
            except:
                logger.error(f'Power supply with address {addr} not found on gpib')
                powerSupplies[addr] = None
    if powerSupplies[addr]:
        powerSupplies[addr].disconnect()
        powerSupplies[addr].close()

def gpib_call(input_message):
    """
    Function to parse gpib requests received over socket, to be sent to correct power supply
    Messages expected to be separated by three colons, with last digits of IP address coming first, and used for addressing the correct power supply
    """
    message=input_message.split(':::')
    addr=message[0]
    logger.info(f"Received message: {input_message}")
    if addr not in powerSupplies:
        logger.error(f"Trying to access unknown address {addr}")
        output = f'Unknown Address {message[0]}'
    else:
        ps = powerSupplies[addr]
        if len(message)<2:
            print('No command specified')
            return ''
        elif message[1]=='Ping':
            try:
                ps.reconnect()
                output=ps.ReadPower()
                ps.disconnect()
                ps.close()
            except:
                output=[-1,-1,-1]
            output=output[0]
        elif message[1]=='ReadPower':
            try:
                ps.reconnect()
                output=ps.ReadPower()
                ps.disconnect()
                ps.close()
            except:
                output=[-1,-1,-1]

        elif message[1]=='SetVoltage':
            ps.reconnect()
            ps.SetLimits(float(message[2]),0.6)
            ps.disconnect()
            ps.close()
            output=f'Setting Voltage {addr} {message[2]}'
        elif message[1]=='TurnOn':
            ps.reconnect()
            ps.TurnOn()
            ps.disconnect()
            ps.close()
            output=f'Turning On {addr}'
        elif message[1]=='TurnOff':
            ps.reconnect()
            ps.TurnOff()
            ps.disconnect()
            ps.close()
            output=f'Turning Off {addr}'
        else:
            print(f'Bad Command {message}')
            output='UNKOWN COMMAND'
    logger.info(f"Returning: {output}")
    return output

port = "5560"
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:%s" % port)

logger.info('-'*30)
logger.info(f"Staring server on port {port}")
logger.info('-'*30)
try:
    while True:
        #  Wait for next request from client
        message = socket.recv_string()
        output=gpib_call(message)
        socket.send_string(f"{output}")
except KeyboardInterrupt:
    socket.close()
    logger.info('-'*30)
    logger.info(f"Stopping server after keyboard interrupt")
    logger.info('-'*30)
except Exception as e:
    socket.close()
    logger.info('-'*30)
    logger.error(f"Received exception {e}")
    logger.error(f"Stopping server")
    logger.info('-'*30)
    
