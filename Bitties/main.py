import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, ListProperty, DictProperty, NumericProperty

from Modules import socket_client

import json
import os
import sys

'''
Connect page is almost entirely build using the python kivy methods, while the game page is almost entirely built using the kivy language in the kv file.
'''
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#Change IP to the public ip address of whatever machine is running the host program, or if running host on same machine, 127.0.0.1
IP = '127.0.0.1'
PORT = 65069

NOHOST = 'Connection error: [WinError 10060] A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed because connected host has failed to respond'

#Info Page will become the active page when an error occurs. It allows you to return to the homescreen.
class InfoPage(GridLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.rows = 2
		self.message = Label(halign='center', valign='middle', font_size=30)
		self.message.bind(width=self.update_text_width)
		self.add_widget(self.message)
		self.return_button = Button(text='Go back', size_hint_x=0.5, size_hint_y=0.2)
		self.return_button.bind(on_press=self.go_back)
		self.add_widget(self.return_button)


	def update_info(self, message):
		self.message.text = message
	def update_text_width(self, *_):
		self.message.text_size = (self.message.width * 0.9, None)
	def go_back(self, *_):
		bitty_app.screen_manager.current = 'Connect'

#The opening screen. Inherits from grid layout. This is where you sign or create an account.
class ConnectPage(GridLayout):

	def __init__(self, **kwargs):
		#super().__init__ runs the init method of whatever is inherited (in this case GridLayout)
		super().__init__(**kwargs)
		#cols and rows in the grid layout
		self.cols = 1
		self.rows = 5

		if os.path.isfile('prev_details.txt'):
			with open('prev_details.txt', 'r') as file:
				prev_username = file.read()
		else:
			prev_username = ''

		#will be used to space out the text input bar
		inputbarlayout = GridLayout(cols=3, size_hint_y=0.25)
		#blank label
		inputbarlayout.add_widget(Label())
		#add username
		self.add_widget(Label(text = 'Username:', color = kivy.utils.get_color_from_hex('#9a1f40'), font_size = 30))
		self.username = TextInput(text=prev_username, width=250, height=30, size_hint=(None,None), multiline=False)
		#adding username to inputbarlayout
		inputbarlayout.add_widget(self.username)
		#and then one more empty label
		inputbarlayout.add_widget(Label())
		self.add_widget(inputbarlayout)

		#will be used to space out the text input bar
		inputbarlayout = GridLayout(cols=3, size_hint_y=0.25)
		#blank label
		inputbarlayout.add_widget(Label())
		#add password
		self.add_widget(Label(text = 'Password:', color = kivy.utils.get_color_from_hex('#9a1f40'), font_size = 30))
		self.password =  TextInput(width=250, height=30, size_hint=(None,None), multiline=False)
		inputbarlayout.add_widget(self.password)
		inputbarlayout.add_widget(Label())
		self.add_widget(inputbarlayout)
		

		#Add the bottom line layout
		bottomline = GridLayout(cols=2)
		#add loginline
		loginline = AnchorLayout(anchor_x='right',anchor_y='bottom')
		self.loginbutton = Button(text='Log In', size_hint_y=0.2, background_normal = '', background_color = kivy.utils.get_color_from_hex('#d9455f'))
		self.loginbutton.bind(on_press=self.login)
		loginline.add_widget(self.loginbutton)
		#add binding
		#add create account line
		createline = AnchorLayout(anchor_x='right',anchor_y='bottom')
		self.createbutton = Button(text='Create Account', size_hint_y=0.2, background_normal = '', background_color = kivy.utils.get_color_from_hex('#d9455f'))
		self.createbutton.bind(on_press=self.createaccount)
		createline.add_widget(self.createbutton)
		#add binding
		bottomline.add_widget(loginline)
		bottomline.add_widget(createline)

		self.add_widget(bottomline)

	def login(self, _):
		ip = IP
		port = PORT
		username = self.username.text

		info = f'Attempting to join as {username}'
		bitty_app.info_screen.update_info(info)
		bitty_app.screen_manager.current = 'Info'

		Clock.schedule_once(self.connect, 1)


	def connect(self, _):
		port = PORT
		ip = IP
		username = self.username.text
		password = self.password.text
		
		if not socket_client.connect(ip, port, username, show_error):
			return

		join_request = 'join;' + username + ';' + password
		self.send_message(join_request)
		socket_client.start_listening(self.receive_join_message, show_error)

	def createaccount(self, _):
		ip = IP
		port = PORT
		username = self.username.text
		password = self.password.text
		if not socket_client.connect(ip, port, username, show_error):

			return

		create_request = 'create;' + username + ';' + password
		self.send_message(create_request)
		socket_client.start_listening(self.receive_create_account_message, show_error)

	def send_message(self, message):
		socket_client.send(message)

	def receive_create_account_message(self, username, message):
		print(message)
		if message == 'already_exists':
			info = f'Sorry, that username already exists.'
			bitty_app.info_screen.update_info(info)
			bitty_app.screen_manager.current = 'Info'
		elif message == 'creation_confirmation':
			self.loaded_indices = {"torsos": 0, "heads": 0, "faces": 0, "hair": 0, "feet": 0, "hands": 0}
			Clock.schedule_once(self.gamepagecreate)

	def receive_join_message(self, username, message):
		print(message)
		if message == 'account_no_exist':
			info = f'Sorry, cannot find username'
			bitty_app.info_screen.update_info(info)
			bitty_app.screen_manager.current = 'Info'
		elif message == 'wrong_password':
			info = f'Sorry, password incorrect'
			bitty_app.info_screen.update_info(info)
			bitty_app.screen_manager.current = 'Info'
		else:
			self.loaded_indices = json.loads(message)
			Clock.schedule_once(self.gamepagecreate)
	#made this because there was a glitch when I just tried to run these oustside of the clock schedule thing with the loaded images turning black
	def gamepagecreate(self, _):
		bitty_app.create_game_page(self.loaded_indices)
		bitty_app.screen_manager.current = 'Game'




##Game Page and bitty widgets
class BittyWidget(Widget):
	#bitty is initialized as transparent
	transparent = NumericProperty(0)

	temp_body_dict = {}

	temp_body_dict['torsos'] = os.listdir('Images/torsos')
	temp_body_dict['heads'] = os.listdir('Images/heads')
	temp_body_dict['faces'] = os.listdir('Images/faces')
	temp_body_dict['hair'] = os.listdir('Images/hair')
	temp_body_dict['feet'] = os.listdir('Images/feet')
	temp_body_dict['hands'] = os.listdir('Images/hands')

	bitty_body_dict = DictProperty(temp_body_dict)

	temp_body_indices = {}

	temp_body_indices['torsos'] = 0
	temp_body_indices['heads'] = 0
	temp_body_indices['faces'] = 0
	temp_body_indices['hair'] = 0
	temp_body_indices['feet'] = 0
	temp_body_indices['hands'] = 0

	bitty_body_indices = DictProperty(temp_body_indices)

class GamePage(Widget):
	friendstring = StringProperty("Search A Friend")
	other_bitty_input = ObjectProperty(None)
	my_bitty_widget = ObjectProperty(None)
	other_bitty_widget = ObjectProperty(None)

	def set_loaded_indices(self, loaded_indices):
		self.my_bitty_widget.bitty_body_indices['torsos'] = loaded_indices['torsos']
		self.my_bitty_widget.bitty_body_indices['faces'] = loaded_indices['faces']
		self.my_bitty_widget.bitty_body_indices['hair'] = loaded_indices['hair']
		self.my_bitty_widget.bitty_body_indices['feet'] = loaded_indices['feet']

		self.my_bitty_widget.transparent = 1

	def set_other_indices(self, loaded_indices):
		self.other_bitty_widget.bitty_body_indices['torsos'] = loaded_indices['torsos']
		self.other_bitty_widget.bitty_body_indices['faces'] = loaded_indices['faces']
		self.other_bitty_widget.bitty_body_indices['hair'] = loaded_indices['hair']
		self.other_bitty_widget.bitty_body_indices['feet'] = loaded_indices['feet']

		self.other_bitty_widget.transparent = 1

	def changeIndex(self, indexname):
		#checking to make sure index stays within list range
		if self.my_bitty_widget.bitty_body_indices[indexname] >= len(self.my_bitty_widget.bitty_body_dict[indexname]) - 1:
			self.my_bitty_widget.bitty_body_indices[indexname] = 0
		else:
			self.my_bitty_widget.bitty_body_indices[indexname] = self.my_bitty_widget.bitty_body_indices[indexname] + 1

	def saveBitty(self):
		indices = json.dumps(self.my_bitty_widget.bitty_body_indices)
		indices = 'save;' + indices
		print(indices)
		self.send_message(indices)

	def fetch_other_bitty(self):
		other_username = self.other_bitty_input.text
		self.friendname = other_username
		fetch_request = "fetch;" + other_username
		self.send_message(fetch_request)
		socket_client.start_listening(self.receive_fetch, show_error)

	def receive_fetch(self, username, message):
		if message == 'account_no_exist':
			self.other_bitty_input.text = "Invalid Username"
		else:
			self.friendstring = self.friendname + "'s Bitty"
			self.other_loaded_indices = json.loads(message)
			self.set_other_indices(self.other_loaded_indices)

	def clear_text_input(self):
		self.other_bitty_input.text = ""

	def send_message(self, message):
		socket_client.send(message)


#The Application class. Inherets from kivy.app.App. Returns a screne manager full of the app screens.
#build is auto run by the app inheritance.
class BittiesApp(App):
	
	def build(self):
		self.screen_manager = ScreenManager()
		#connection page
		self.connect_screen = ConnectPage()
		screen = Screen(name='Connect')
		screen.add_widget(self.connect_screen)
		self.screen_manager.add_widget(screen)
		#info page
		self.info_screen = InfoPage()
		screen = Screen(name='Info')
		screen.add_widget(self.info_screen)
		self.screen_manager.add_widget(screen)

		return self.screen_manager

	def create_game_page(self,loaded_indices):
		self.game_screen = GamePage()

		self.game_screen.set_loaded_indices(loaded_indices)

		screen = Screen(name='Game')
		screen.add_widget(self.game_screen)
		self.screen_manager.add_widget(screen)

def show_error(err_message):
	bitty_app.info_screen.update_info(err_message)
	print(err_message)
	bitty_app.screen_manager.current = 'Info'

if __name__ == "__main__":
	bitty_app = BittiesApp()
	bitty_app.run()