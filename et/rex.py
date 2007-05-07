class offer(object):
	"""A Data structure for holding participant offers"""
	def __init__(self, toParticipant, fromParticipant, amount):
		self.fromParticipant = fromParticipant
		self.toParticipant = toParticipant
		self.amount = amount
		self.timestamp = time()


class rexParameters(object):
	"""A Data structure for holding parameters"""
	def __init__(self, 	AvailablePoints = "Available Points",
						AvailablePointsValue = "50",
						PromptText = "Prompt Text",
						PromptTextValue = "The experimenter gave you 25 points to offer this round. Select a player below to make an offer to that player",
						ParticipantsLabel = "Participants Label",
						ParticipantsLabelValue = "Make offer to: ",
						AmountLabel = "Amount Label",
						AmountLabelValue = "Offer amount: ",
						SubmitLabel = "Submit Label",
						SubmitLabelValue = "Submit Offer",
						WaitingText = "Waiting Text",
						WaitingTextValue = "Waiting for other players...",
						AcceptText = "Accept Text",
						AcceptTextValue = "Listed below are offers you received.",
						AcceptButtonLabel = "Accept Button Label ",
						AcceptButtonLabelValue = "Continue" 
					):
		self.AvailablePoints = AvailablePoints
		self.AvailablePointsValue = AvailablePointsValue
		self.PromptText = PromptText
		self.PromptTextValue = PromptTextValue
		self.ParticipantsLabel = ParticipantsLabel
		self.ParticipantsLabelValue = ParticipantsLabelValue
		self.AmountLabel = AmountLabel
		self.AmountLabelValue = AmountLabelValue
		self.SubmitLabel = SubmitLabel
		self.SubmitLabelValue = SubmitLabelValue
		self.WaitingText = WaitingText
		self.WaitingTextValue = WaitingTextValue
		self.AcceptText = AcceptText
		self.AcceptTextValue = AcceptTextValue
		self.AcceptButtonLabel = AcceptButtonLabel
		self.AcceptButtonLabelValue = AcceptButtonLabelValue