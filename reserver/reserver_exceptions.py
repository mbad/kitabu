class OverlappingReservations(Exception):
	def __init__(self, reservations):
		self.reservations = reservations