import serial
import serial.tools.list_ports as list_ports
import string
import time
import json
import PySimpleGUI as sg
sg.ChangeLookAndFeel('Reddit')

# CH340 product ID
USB_product_ID 	= 29987
device 			= None
delayOnToken 	= '>'
delayOffToken 	= '<'

# times to try to connect to uart 
triesToConnect_UART = 10
uartSuccess = False

def get_com_list():
	ports = list(serial.tools.list_ports.comports())
	for p in ports:
		if p.pid == USB_product_ID:
			return p.device

def serial_init(port, device):
	counter = 0
	global uartSuccess
	if port:
		while hasattr(device, 'close') is False:
			try:
				device = serial.Serial(port, 9600, timeout= 5)
				# print('uart succesfully initialized')
				while device.readline().decode("utf-8")[0] != '>':
					print('waiting token')
				uartSuccess = True
				time.sleep(1.5)
			except serial.SerialException: 
				print('trying to connect')
				time.sleep(0.1)
				counter += 1
				if counter == triesToConnect_UART:
					print('Check device selection')
					break
		return device

def dont_fry_me_plz():
	if device:
		device.write((delayOnToken + '0').encode())
		device.write((delayOffToken + '1000').encode())


layout = [  
			[sg.Button('Connect')],
			[sg.Text('On time:'), sg.In(size=(8,1), key='onTime'), sg.Text('waiting', key='labelOn'), sg.Text('[ms]')],
			[sg.Text('Off time:'), sg.In(size=(8,1), key='offTime'), sg.Text('waiting', key='labelOff'), sg.Text('[ms]')],
			[sg.Button('Send', disabled = True), sg.Button('Stop', disabled = True)]
        ]

window = sg.Window('Solenoid Control 1.1', layout)

while True:
	event, values = window.read()
	# print(event, values)

	if event is None:
		break

	# uart connect 
	if event == 'Connect':
		device = serial_init(get_com_list(), device)
		if uartSuccess is True:
			window.Element('Connect').Update(disabled=True)
			window.Element('Send').Update(disabled=False)
			window.Element('Stop').Update(disabled=False)
			window.Element('Connect').Update('Connected')
		else:
			window.Element('Connect').Update(disabled=True)
			window.Element('Connect').Update('Check Serial')

	# send values, will catch empty cells and send always off solenoid 
	if event == 'Send':
		if not values['onTime'] or not values['offTime']:
			dont_fry_me_plz()

		if not (int(values['onTime'].isdigit())) or (int(values['onTime'])) > 10000:
			values['onTime'] = '0'

		if not (int(values['offTime'].isdigit())) or (int(values['offTime'])) > 10000:
			values['offTime'] = '1000'

		if (int(values['onTime']) <= 30):
			values['onTime'] = '60'

		if (int(values['offTime']) <= 30):
			values['offTime'] = '30'

		device.write((delayOnToken + values['onTime']).encode())
		device.write((delayOffToken   + values['offTime']).encode())
		window.Element('labelOn').Update(values['onTime'])
		window.Element('labelOff').Update(values['offTime'])

	if event == 'Stop':
		dont_fry_me_plz()

# if user closes, switch off solenoid 
window.close()
if device:
	dont_fry_me_plz()
	device.close()

# pyinstaller --onefile --noconsole --icon=gear.ico demo_gui.py
