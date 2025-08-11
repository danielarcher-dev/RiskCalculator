
import accounts.instrument as instrument

class Orders():

    def __init__(self, dataframe):
        self.OrderData = dataframe
        self.Orders = [Order(item) for item in dataframe]

class Order():
    def __init__(self, item):
        self.Order = item
        self.orderId = item['orderId']
        self.session = item['session']
        self.duration = item['duration']
        self.orderType = item['orderType']
        self.complexOrderStrategyType = item['complexOrderStrategyType']
        self.quantity = item['quantity']
        self.filledQuantity = item['filledQuantity']
        self.remainingQuantity = item['remainingQuantity']
        self.requestedDestination = item['requestedDestination']
        self.destinationLinkName = item['destinationLinkName']
        try:
            self.price = item['price']
        except:
            self.price = None
            # print("{0} has no price, {1}".format(self.orderId, self.orderType))
        if self.orderType == "STOP":
            self.stopPrice = item['stopPrice']
            self.stopType = item['stopType']
        try:
            self.stopPrice = item['stopPrice']
        except:
            self.stopPrice = 0
        self.OrderLegs = [OrderLeg(leg) for leg in item['orderLegCollection']]
        self.orderStrategyType = item['orderStrategyType']
        self.cancelable = item['cancelable']
        self.editable = item['editable']
        self.status = item['status']
        self.enteredTime = item['enteredTime']
        try:
            self.closeTime = item['closeTime']
        except:
            self.closeTime = None
            # print("{0} has no closeTime, {1}".format(self.orderId, self.orderType))
        self.tag = item['tag']
        self.accountNumber = item['accountNumber']
        # self.orderActivityCollection = item['orderActivityCollection']
        try:
            self.orderActivityCollection = [OrderActivity(activity) for activity in item['orderActivityCollection']]
        except:
            self.orderActivityCollection = None

class OrderLeg():
    def __init__(self, item):
        self.OrderLeg = item
        self.orderLegType = item['orderLegType']
        self.legId = item['legId']
        self.instrument = instrument.Instrument(item['instrument'])
        self.instruction = item['instruction']
        self.positionEffect = item['positionEffect']
        self.quantity = item['quantity']

class OrderActivity():
    def __init__(self, item):
        self.OrderActivity = item
        self.activityType = item['activityType']
        self.activityId = item['activityId']
        self.executionType = item['executionType']
        self.quantity = item['quantity']
        self.orderRemainingQuantity = item['orderRemainingQuantity']
        self.executionLegs = item['executionLegs']
        self.executionLegs = [ExecutionLeg(leg) for leg in item['executionLegs']]

class ExecutionLeg():
    def __init__(self, item):
        self.ExecutionLeg = item
        self.legId = item['legId']
        self.quantity = item['quantity']
        self.mismarkedQuantity = item['mismarkedQuantity']
        self.price = item['price']
        self.time = item['time']
        self.instrumentId = item['instrumentId']