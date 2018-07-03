"""
Description : A Python implementation of the Apriori Algorithm

Usage:
    $python aprioriAnalytics.py
"""

from itertools import chain, combinations
from collections import defaultdict
from firebase.firebase import FirebaseApplication
from firebase.firebase import FirebaseAuthentication
from datetime import datetime

def subsets(arr):

    """ 
    Returns non empty subsets of arr

    enumerate(arr)       <= returns the following format "<index>, <array element>"
    combinations(arr, i) <= returns all i-length combinations of the array.
    chain(arr)           <= unpackas a list of lists

    """
    return chain(*[combinations(arr, i + 1) for i, a in enumerate(arr)])


def returnItemsWithMinSupport(itemSet, transactionList, minSupport, freqSet):
        """
        calculates the support for items in the itemSet and returns a subset
        of the itemSet each of whose elements satisfies the minimum support
        """
        _itemSet = set()
        localSet = defaultdict(int)

        for item in itemSet:
                for transaction in transactionList:
                        if item.issubset(transaction):
                                freqSet[item] += 1
                                localSet[item] += 1

        for item, count in localSet.items():
                support = float(count)/len(transactionList)

                if support >= minSupport:
                        _itemSet.add(item)

        return _itemSet


def joinSet(itemSet, length):
        """Join a set with itself and returns the n-element itemsets"""
        return set([i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == length])


def getItemSetTransactionList(data_iterator):

    """

    Takes data from dataFromFile() and returns list of items and a list of transactions
    and generate two seperate sets of items and transactions.

    The item list would be: 
    ([frozenset(['apple']), frozenset(['beer']), frozenset(['chicken']), etc

    The transaction list would be:
    frozenset(['beer', 'rice', 'apple', 'chicken']), frozenset(['beer', 'rice', 'apple']), etc

    """
    transactionList = list()
    itemSet = set()
    for record in data_iterator:
        transaction = frozenset(record)
        transactionList.append(transaction)
        for item in transaction:
            itemSet.add(frozenset([item]))              # Generate 1-itemSets
    #print(transactionList)
    #print(itemSet)
    return itemSet, transactionList
    


def runApriori(data_iter, minSupport, minConfidence):
    """
    run the apriori algorithm. data_iter is a record iterator
    Return both:
     - items (tuple, support)
     - rules ((pretuple, posttuple), confidence)
    """
    itemSet, transactionList = getItemSetTransactionList(data_iter)

    freqSet = defaultdict(int)
    largeSet = dict()
    # Global dictionary which stores (key=n-itemSets,value=support)
    # which satisfy minSupport

    assocRules = dict()
    # Dictionary which stores Association Rules

    oneCSet = returnItemsWithMinSupport(itemSet,
                                        transactionList,
                                        minSupport,
                                        freqSet)

    currentLSet = oneCSet
    k = 2
    while(currentLSet != set([])):
        largeSet[k-1] = currentLSet
        currentLSet = joinSet(currentLSet, k)
        currentCSet = returnItemsWithMinSupport(currentLSet,
                                                transactionList,
                                                minSupport,
                                                freqSet)
        currentLSet = currentCSet
        k = k + 1

    def getSupport(item):
            """local function which Returns the support of an item"""
            return float(freqSet[item])/len(transactionList)

    toRetItems = []
    for key, value in largeSet.items():
        toRetItems.extend([(tuple(item), getSupport(item))
                           for item in value])

    toRetRules = []
    for key, value in list(largeSet.items())[1:]:
        for item in value:
            _subsets = map(frozenset, [x for x in subsets(item)])
            for element in _subsets:
                remain = item.difference(element)
                if len(remain) > 0:
                    confidence = getSupport(item)/getSupport(element)
                    if confidence >= minConfidence:
                        toRetRules.append(((tuple(element), tuple(remain)),
                                           confidence))
    return toRetItems, toRetRules


"""def printResults(items, rules):
    #prints the generated itemsets sorted by support and the confidence rules sorted by confidence
    #for item, support in sorted(items, key=lambda(item, support): support):
    #for item, support in sorted(items, key=operator.itemgetter(1)):
    for item, support in sorted(items, key=lambda support: support[1])
        print("item: %s , %.3f" % (str(item), support))
    print("\n------------------------ RULES:")
    #for rule, confidence in sorted(rules, key=lambda (rule, confidence): confidence):
    #for rule, confidence in sorted(rules, key=operator.itemgetter(1)):
    for item, support in sorted(items, key=lambda confidence: confidence[1])
        pre, post = rule
        print("Rule: %s ==> %s , %.3f" % (str(pre), str(post), confidence))"""


def dataFromFile(fname):
        """
        Function which reads from the file and yields a generator of frozen sets of each line in the csv

        The first line of tesco.csv file returns the following output:
        frozenset(['beer', 'rice', 'apple', 'chicken'])
        """
        file_iter = open(fname, 'rU')
        for line in file_iter:
                line = line.strip().rstrip(',')                         # Remove trailing comma
                record = frozenset(line.split(','))
                yield record

def toSort(a):
    return a[1]

if __name__ == "__main__":
    
    auth = FirebaseAuthentication('<FIREBASE AUTH KEY>', '<GMAIL ID>')
    app = FirebaseApplication('<LINK TO FIREBASE APP>', authentication=auth)
    products = app.get('/product', None)
    productList = {}
    if(products):
        for product,details in products.items():
            productList[product] = [details['name'],details['cost']]

    result = app.get('/user', None)
    month = int(input("Enter the month from which analysis is to be made: "))
    year = int(input("Enter the year from which analysis has to be made: "))
    monthsToAnalyse = int(input("Enter the number of months for which the analysis has to be done: "))
    productsArray = []
    if(result):
        while(monthsToAnalyse):
            analysisMonth = str(month)+'_'+str(year)
            #print(analysisMonth)
            for user,details in result.items():
                if(analysisMonth in details.keys()):
                    productsArray.append(list(details[analysisMonth].keys()))
            monthsToAnalyse = monthsToAnalyse - 1
            month = month + 1
            if(month == 13):
                year = year + 1
                month = 1
    if(len(productsArray)):
        minSupport = float(input("Enter the minimum support required: "))
        minConfidence = float(input("Enter the minimum confidence required: "))
        items, rules = runApriori(productsArray, minSupport, minConfidence)        
        sortedRules = sorted(rules, key=toSort, reverse=True)
        
        if(len(sortedRules)):
            i = 1
            print("\n\n######################################################\n\n")
            possibleOfferList = []
            for rule in sortedRules:
                print(i,end=") ")
                for itemsTuple in rule[0]:            
                    possibleOfferList.append([])
                    for items in itemsTuple:
                        print(productList[items][0],end=", ")
                        possibleOfferList[i-1].append(items)
                    print(end=" => ")
                i = i+1
                print(rule[1])
            
            print("\n\n######################################################\n\n")
            offerCondition = input("Enter 'c' to select the offer: ")
            offerList = []
            
            while(offerCondition == 'c'):
                i = int(input("Enter the rule number to add the offer: "))
                print("\n----------------------------------------------------------------------------------------\n")
                print("Cost of: ",end="")
                sum_ = 0        
                for item in possibleOfferList[i-1]:
                    print(productList[item][0],"(",productList[item][1],")",end=", ")
                    sum_ = sum_ + int(productList[item][1])
                print("is : ",sum_)
                print("\n----------------------------------------------------------------------------------------\n")
                sum_ = 0
                costDict = {}
                for item in possibleOfferList[i-1]:
                    new_cost = int(input("Enter the new cost of: "+productList[item][0]+": "))            
                    costDict[item] = int(productList[item][1]) - new_cost
                    sum_ = sum_ + new_cost 
                offerList.append(costDict)        
                
                offerCondition = input("Enter 'c' to select another the offer and 'q' to quit: ")        
                print("\n=========================================================================================\n")
                
            print("\n----------------------------------------------------------------------------------------\n")            
            counter = 0
            for offers in offerList:            
                key = '/offers/'+str(datetime.now().month)+"_"+str(datetime.now().year)+"/offer"+str(counter)
                app.put('', key, offers)
                print("New Cost of: ",end="")          
                for item in offers.keys():
                    print(productList[item][0],"(",int(productList[item][1]) - offers[item],")",end=", ")
                print("is : ",sum_)                   
                counter = counter + 1
            print("\n----------------------------------------------------------------------------------------\n")
        else:
            print("\n\nNo rule is found for the given pair of support and confident thresholds. Try lowering the values or change the period of analysis\n")
    else:
        print("\n\nNo data is found during the specied interval.\n")
