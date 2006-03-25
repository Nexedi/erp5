
class Node:
    pass


def testAmount1(self):
  node = Node()
  node._capacity_item_list = [
    [['a', 2]],
    [['b', 5]],
    ]
  amount_list = [
    ['b', 1],
    ['a', 1],
    ]
  return repr(self.portal_simulation.isAmountListInsideCapacity(node, amount_list))

def getCategory(self, relative_url):
#  return self.portal_categories.resolveCategory(relative_url)
  return self.portal_categories.restrictedTraverse(relative_url)


def testAmount3(self):
  node = Node()
  node._capacity_item_list = [
    [[getCategory(self, 'skill/Assistant/Bebe'), 10]],
    [[getCategory(self, 'skill/Assistant/Enfant'), 10]],
    ]
  amount_list = [
    [getCategory(self, 'skill/Assistant'), 8]
    ]
  return repr(self.portal_simulation.isAmountListInsideCapacity(node, amount_list, getCategory(self, 'skill'), 1))

def testAmount4(self):
  node = Node()
  node._capacity_item_list = [
    [[getCategory(self, 'skill/Assistant'), 10]],
    ]
  amount_list = [
    [getCategory(self, 'skill/Assistant/Bebe'), 10],
    [getCategory(self, 'skill/Assistant/Enfant'), 10],
    ]
  return repr(self.portal_simulation.isAmountListInsideCapacity(node, amount_list, getCategory(self, 'skill'), 1))
