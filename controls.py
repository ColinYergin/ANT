import pygame

class Controls:
	def __init__(self):
		self.while_pressed_handlers = {}
		self.on_event_handlers = {}
	def while_pressed(self, key, cb):
		self.while_pressed_handlers[key] = cb
	def on_event(self, etype, cb):
		self.on_event_handlers[etype] = cb
	def run(self):
		for event in pygame.event.get():
			if event.type in self.on_event_handlers:
				self.on_event_handlers[event.type](event)
		pressed = pygame.key.get_pressed()
		for k, cb in self.while_pressed_handlers.items():
			if pressed[k]: cb()