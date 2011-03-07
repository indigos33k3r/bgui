"""

This module defines the following constants:

*InputText options*
  * BGUI_INPUT_NONE = 0
  * BGUI_INPUT_SELECT_ALL = 1

  * BGUI_INPUT_DEFAULT = BGUI_INPUT_NONE

"""

from .widget import *
from .label import *
from .frame import *

import blf
import time

# InputText options
BGUI_INPUT_NONE = 0
BGUI_INPUT_SELECT_ALL = 1

BGUI_INPUT_DEFAULT = BGUI_INPUT_NONE

class TextInput(Widget):
	"""Widget for getting text input"""
	theme_section = 'TextInput'
	theme_options = {'TextColor', 'FrameColor', 'BorderSize', 'BorderColor', 'HighlightColor',
						'InactiveTextColor', 'InactiveFrameColor', 'InactiveBorderSize', 'InactiveBorderColor', 'InactiveHighlightColor'}

	def __init__(self, parent, name, text="", prefix="", font=None, pt_size=30, color=(1, 1, 1, 1),
					aspect=None, size=[0, 0], pos=[0, 0], sub_theme='',input_options=BGUI_INPUT_DEFAULT, options=BGUI_DEFAULT):
		"""The TextInput constructor

		Arguments:

		parent -- the widget's parent
		name -- the name of the widget
		text -- the text to display (this can be changed later via the text property)
		prefix -- prefix text displayed before user input, cannot be edited by user (this can be changed later via the prefix property)
		font -- the font to use
		pt_size -- the point size of the text to draw
		color -- color of the font for this widget
		aspect -- constrain the widget size to a specified aspect ratio
		size -- a tuple containing the wdith and height
		pos -- a tuple containing the x and y position
		sub_theme -- sub theme to be applied to this widget
		options -- various other options

		"""
		
		Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)
		
		self.text_prefix = prefix
		self.pos = len(text)
		self.input_options = input_options
		self.colors = {}
		
		#create widgets
		self.frame = Frame(self, name+"_frame", size=[1,1], options = BGUI_NO_FOCUS | BGUI_DEFAULT | BGUI_CENTERY)
		self.highlight = Frame(self, name+"_highlight", size=self.frame.size, options = BGUI_NO_FOCUS | BGUI_CENTERY)
		self.cursor = Frame(self, name+"_cursor", size=[1,1], border=0, options = BGUI_NO_FOCUS | BGUI_CENTERY)
		self.label = Label(self, name+"_label", text, font, pt_size, options = BGUI_NO_FOCUS | BGUI_NORMALIZED )
		
		#Color and setting initialization
		self.colormode = 0
		
		if self.theme:
			self.colors["text"] = [None, None]
			self.colors["text"][0] = [float(i) for i in self.theme.get(self.theme_section, 'InactiveTextColor').split(',')]
			self.colors["text"][1] = [float(i) for i in self.theme.get(self.theme_section, 'TextColor').split(',')]
			
			self.colors["frame"] = [None, None]
			self.colors["frame"][0] = [float(i) for i in self.theme.get(self.theme_section, 'InactiveFrameColor').split(',')]
			self.colors["frame"][1] = [float(i) for i in self.theme.get(self.theme_section, 'FrameColor').split(',')]
			
			self.colors["border"] = [None, None]
			self.colors["border"][0] = [float(i) for i in self.theme.get(self.theme_section, 'InactiveBorderColor').split(',')]
			self.colors["border"][1] = [float(i) for i in self.theme.get(self.theme_section, 'BorderColor').split(',')]
			
			self.colors["highlight"] = [None, None]
			self.colors["highlight"][0] = [float(i) for i in self.theme.get(self.theme_section, 'HighlightColor').split(',')]
			self.colors["highlight"][1] = [float(i) for i in self.theme.get(self.theme_section, 'HighlightColor').split(',')]
			
			self.border_size = [None, None]
			self.border_size[0] = float(self.theme.get(self.theme_section, 'InactiveBorderSize'))
			self.border_size[1] = float(self.theme.get(self.theme_section, 'BorderSize'))
			
		else:
			self.colors["text"] = [None, None]
			self.colors["text"][0] = self.colors["text"][1] = [1, 1, 1, 1]
			
			self.colors["frame"] = [None, None]
			self.colors["frame"][0] = self.colors["frame"][1] = [0, 0, 0, 0]
			
			self.colors["border"] = [None, None]
			self.colors["border"][0] = self.colors["border"][1] = [0, 0, 0, 0]
			
			self.colors["highlight"] = [None, None]
			self.colors["highlight"][0] = self.colors["highlight"][1] = [0.6, 0.6, 0.6, 0.5]
			
			self.border_size = [0, 0]
			
		self.swapcolors(0)
			
		#gauge height of the drawn font
		fd = blf.dimensions(self.label.fontid, "Egj/}|^,") 
		
		py = .5- (fd[1]/self.size[1]/2)
		px = fd[1]/self.size[0] - fd[1]/1.5/self.size[0]
		self.label.position = [px, py]
		self.fd = blf.dimensions(self.label.fontid, self.text_prefix )[0] + fd[1]/3.2

		self.frame.size = [1,1] 
		self.frame.position = [0, 0]
		
		self.slice = [len(text), len(text)]
		self.slice_direction = 0
		self.mouse_slice_start = 0
		self.mouse_slice_end = 0
		#create the char width list
		self.char_widths = []
		for char in self.text:
			self.char_widths.append( blf.dimensions(self.label.fontid, char*20 )[0]/20 )
		
		#initial call to update_selection
		self.selection_refresh = 1
		self.just_activated = 0
		self._active = 0 #internal active state to avoid confusion from parent active chain
		
		#blinking cursor
		self.time = time.time()
		
		#double/triple click functionality
		self.click_counter = 0
		self.single_click_time = 0.0
		self.double_click_time = 0.0
		
		# On Enter callback
		self.on_enter_key = None
		
	@property
	def text(self):
		return self.label.text
	
	@text.setter
	def text(self, value):
		self.label.text = value
	
	@property
	def prefix(self):
		return self.text_prefix
	
	@prefix.setter
	def prefix(self, value):
		self.fd = blf.dimensions(self.label.fontid, value)[0] + fd[1]/3.2
		self.text_prefix = value
		
	
	
	
	
	
	#Activation Code
	def activate(self):
		if self.frozen:
			return
		self.system.focused_widget = self
		self.swapcolors(1)
		self.colormode = 1
		if self.input_options & BGUI_INPUT_SELECT_ALL:
			self.slice = [0, len(self.text)]
			self.slice_direction = -1
		self.just_activated = 1
		self._active = 1
		
	def deactivate(self):
		self.system.focused_widget = 0
		self.swapcolors(0)
		self.colormode = 0
		self.just_activated = 0
		self._active = 0
	
	def swapcolors(self, state = 0): #0 inactive 1 active
		
		self.frame.colors = [self.colors["frame"][state]] *4
		self.frame.border = self.border_size[state]
		self.frame.border_color = self.colors["border"][state]
		self.highlight.colors = [self.colors["highlight"][state]] *4
		self.label.color = self.colors["text"][state]	
			
		if state == 0:
			self.cursor.colors = [[0.0,0.0,0.0,0.0]] *4
		else:
			self.cursor.colors = [self.colors["text"][state]] *4

	
	
	
	
	
	#Selection Code
	def update_selection(self):
		left = self.fd + blf.dimensions(self.label.fontid, self.text[:self.slice[0]] )[0]
		right = self.fd + blf.dimensions(self.label.fontid, self.text[:self.slice[1]] )[0]
		self.highlight.position = [ left, 1]
		self.highlight.size = [right-left, self.frame.size[1]*.8 ]
		if self.slice_direction in [ 0, -1 ]:
			self.cursor.position = [ left, 1]
		else:
			self.cursor.position = [ right, 1]
		self.cursor.size = [2, self.frame.size[1]*.8 ]

	def find_mouse_slice(self, pos):
		cmc = self.calc_mouse_cursor(pos)
		mss = self.mouse_slice_start
		self.mouse_slice_end = cmc

		if cmc < mss:
			self.slice_direction = -1
			self.slice = [self.mouse_slice_end, self.mouse_slice_start]
		elif cmc > mss:
			self.slice_direction = 1
			self.slice = [self.mouse_slice_start, self.mouse_slice_end]
		else:
			self.slice_direction = 0
			self.slice = [self.mouse_slice_start, self.mouse_slice_start]
		self.selection_refresh = 1
	
	def calc_mouse_cursor(self, pos):
		adj_pos = pos[0] - ( self.position[0]+self.fd )
		find_slice = 0
		i = 0
		for entry in self.char_widths:
			if find_slice + entry > adj_pos:
				if abs(( find_slice + entry ) - adj_pos) >= abs(adj_pos - find_slice):
					return i
				else:
					return i+1
			else:
				find_slice += entry
			i += 1
		
		self.time = time.time() - 0.501
		
		return i
	
	
	
	
	def _handle_mouse(self, pos, event):
		"""Extend function's behaviour by providing focus to unfrozen inactive TextInput,
		swapping out colors.
		"""
		if self.frozen:
			return
		
		
			
		if event == BGUI_MOUSE_CLICK:
			
			self.mouse_slice_start = self.calc_mouse_cursor(pos)
			
			if not self._active:
				self.activate()
			
			if not self.input_options & BGUI_INPUT_SELECT_ALL:
				self.find_mouse_slice(pos)
				

		elif event == BGUI_MOUSE_ACTIVE:
			if not self.just_activated or self.just_activated and not self.input_options & BGUI_INPUT_SELECT_ALL:
				self.find_mouse_slice(pos)
			
				
		if event == BGUI_MOUSE_RELEASE:
			
			self.selection_refresh = 1
			if self.slice[0] == self.slice[1]:
				self.slice_direction = 0
			self.just_activated = 0
			
			#work out single / double / triple clicks
			if self.click_counter == 0:
				self.single_click_time = time.time()
				self.click_counter = 1
			elif self.click_counter == 1:
				if time.time() - self.single_click_time < .2:
					self.click_counter = 2
					self.double_click_time = time.time()
					words = self.text.split(" ")
					i = 0
					for entry in words:
						if self.slice[0] < i+len(entry):
							self.slice = [i, i + len(entry) + 1]
							break
						i += len(entry) + 1
				else:
					self.click_counter = 1
					self.single_click_time = time.time()
			elif self.click_counter == 2:
				if time.time() - self.double_click_time < .2:
					self.click_counter = 3
					self.slice = [0, len(self.text)]
					self.slice_direction = -1
				else:
					self.click_counter = 1
					self.single_click_time = time.time()
			elif self.click_counter == 3:
				self.single_click_time = time.time()
				self.click_counter = 1
			
			self.time = time.time()

		Widget._handle_mouse(self, pos, event)

	
	
	
	
	
	
	def _handle_key(self, key, is_shifted):
		"""Handle any keyboard input"""
		
		
		# Try char to int conversion for alphanumeric keys... kinda hacky though
		try:
			key = ord(key)
		except:
			pass
			
		if is_shifted:
			sh = 0 #used for slicing
		else:
			sh = 1
		slice_len = abs(self.slice[0] - self.slice[1])
		x, y = 0,0
		
		
		
		if key == BACKSPACEKEY:
			if slice_len != 0:
				self.text = self.text[:self.slice[0]] + self.text[self.slice[1]:]
				self.char_widths = self.char_widths[:self.slice[0]] + self.char_widths[self.slice[1]:]
				self.slice = [self.slice[0], self.slice[0]]
				#handle char length list
			elif self.slice[0] > 0:
				self.text = self.text[:self.slice[0]-1] + self.text[self.slice[1]:]
				self.slice = [self.slice[0]-1, self.slice[1]-1]
				
				
		elif key == LEFTARROWKEY:
			slice_len = abs(self.slice[0]-self.slice[1])
			if ( self.slice_direction in [-1, 0] ):
				if is_shifted and self.slice[0] > 0:
					self.slice = [self.slice[0]-1, self.slice[1]]
					self.slice_direction = -1
				elif is_shifted:
					pass
				else:
					if slice_len > 0: #
						self.slice = [self.slice[0], self.slice[0]]
					elif self.slice[0] > 0:
						self.slice = [self.slice[0]-1, self.slice[0]-1]
					self.slice_direction = 0
						
			elif self.slice_direction == 1:
				if is_shifted :
					self.slice = [self.slice[0], self.slice[1]-1]
				else:
					self.slice = [self.slice[0], self.slice[0]]
				if self.slice[0]-self.slice[1] == 0:
					self.slice_direction = 0
			
				
		elif key == RIGHTARROWKEY:
			slice_len = abs(self.slice[0]-self.slice[1])
			if ( self.slice_direction in [1, 0] ):
				if is_shifted  and self.slice[1] < len(self.text):
					self.slice = [self.slice[0], self.slice[1]+1]
					self.slice_direction = 1
				elif is_shifted:
					pass
				else:
					if slice_len > 0:
						self.slice = [self.slice[1], self.slice[1]]
					elif self.slice[1] < len(self.text):
						self.slice = [self.slice[1]+1, self.slice[1]+1]
					self.slice_direction = 0
			elif self.slice_direction == -1:
				if is_shifted:
					self.slice = [self.slice[0]+1, self.slice[1]]
				else:
					self.slice = [self.slice[1], self.slice[1]]
				if self.slice[0]-self.slice[1] == 0:
					self.slice_direction = 0
		else:
			char = None
			if ord(AKEY) <= key <= ord(ZKEY):
				if is_shifted: char = chr(key - 32)
				else: char = chr(key)
				
			elif ord(ZEROKEY) <= key <= ord(NINEKEY):
				if not is_shifted: char = chr(key)
				else:
					key = chr(key)
					if key == ZEROKEY: char = ")"
					elif key == ONEKEY: char = "!"
					elif key == TWOKEY: char = "@"
					elif key == THREEKEY: char = "#"
					elif key == FOURKEY: char = "$"
					elif key == FIVEKEY: char = "%"
					elif key == SIXKEY: char = "^"
					elif key == SEVENKEY: char = "&"
					elif key == EIGHTKEY: char = "*"
					elif key == NINEKEY: char = "("
					
			elif PAD0 <= key <= PAD9:
				char = str(key-PAD0)
			elif key == PADPERIOD: char = "."
			elif key == PADSLASHKEY: char = "/"
			elif key == PADASTERKEY: char = "*"
			elif key == PADMINUS: char = "-"
			elif key == PADPLUSKEY: char = "+"
			elif key == SPACEKEY: char = " "
			#elif key == TABKEY: char = "\t"
			elif key in (ENTERKEY, PADENTER):
				if self.on_enter_key:
					self.on_enter_key(self)
			elif not is_shifted:
				if key == ACCENTGRAVEKEY: char = "`"
				elif key == MINUSKEY: char = "-"
				elif key == EQUALKEY: char = "="
				elif key == LEFTBRACKETKEY: char = "["
				elif key == RIGHTBRACKETKEY: char = "]"
				elif key == BACKSLASHKEY: char = "\\"
				elif key == SEMICOLONKEY: char = ";"
				elif key == QUOTEKEY: char = "'"
				elif key == COMMAKEY: char = ","
				elif key == PERIODKEY: char = "."
				elif key == SLASHKEY: char = "/"
			else:
				if key == ACCENTGRAVEKEY: char = "~"
				elif key == MINUSKEY: char = "_"
				elif key == EQUALKEY: char = "+"
				elif key == LEFTBRACKETKEY: char = "{"
				elif key == RIGHTBRACKETKEY: char = "}"
				elif key == BACKSLASHKEY: char = "|"
				elif key == SEMICOLONKEY: char = ":"
				elif key == QUOTEKEY: char = '"'
				elif key == COMMAKEY: char = "<"
				elif key == PERIODKEY: char = ">"
				elif key == SLASHKEY: char = "?"
				
			if char:
				#need option to limit text to length of box
				#need to replace all selected text with new char
				#need copy place somewhere
				
				self.text = self.text[:self.slice[0]] + char + self.text[self.slice[1]:]
				self.char_widths = self.char_widths[:self.slice[0]] + [ blf.dimensions(self.label.fontid, char*20 )[0]/20 ] + self.char_widths[self.slice[1]:]
				self.slice = [self.slice[0]+1, self.slice[0]+1]
				self.slice_direction = 0
				
		#update selection widgets after next draw call
		self.selection_refresh = 1
		
		#ensure cursor is not hidden
		self.time = time.time()
	
	
	
	
	
	def _draw(self):
		temp = self.text
		
		if self == self.system.focused_widget and self._active == 0:
			self.activate()
		
		self.text = self.text_prefix + self.text
		
		# Now draw the children
		Widget._draw(self)
		
		self.label.text = temp
		
		if self.colormode == 1 and self.system.focused_widget != self:
			self._active = 0
			self.swapcolors(0)
			self.virgin = 1
			self.colormode = 0
		
		#selection code needs to be called after draw, which is tracked internally to TextInput
		if self.selection_refresh == 1:
			self.update_selection()
			self.selection_refresh = 0
			
		#handle blinking cursor
		if self.slice[0]-self.slice[1] == 0 and self._active:
			if time.time() - self.time > 1.0:
				self.time = time.time()
			
			elif time.time() - self.time > 0.5:
				self.cursor.colors = [[0.0,0.0,0.0,0.0]] *4
			else:
				self.cursor.colors = [self.colors["text"][1]] *4
		else:
			self.cursor.colors = [[0.0,0.0,0.0,0.0]] *4