'''
Created on Apr 12, 2013

@author: rega
'''
import numpy as np
from threading import Thread

# for brevity, we omit transposing two characters. Only inserts,
# removals, and substitutions are considered here.
def levenshtein_dyn(word1, word2):
    """
    Levenshtein dynamic programming implementation
    """
    columns = len(word1) + 1
    rows = len(word2) + 1

    # build first row
    currentRow = [0]
    for column in xrange(1, columns):
        currentRow.append(currentRow[column - 1] + 1)

    for row in xrange(1, rows):
        previousRow = currentRow
        currentRow = [ previousRow[0] + 1 ]

        for column in xrange(1, columns):

            insertCost = currentRow[column - 1] + 1
            deleteCost = previousRow[column] + 1

            if word1[column - 1] != word2[row - 1]:
                replaceCost = previousRow[ column - 1 ] + 1
            else:                
                replaceCost = previousRow[ column - 1 ]

            currentRow.append(min(insertCost, deleteCost, replaceCost))

    return currentRow[-1]


class TrieNode:
    """
    The Trie data structure keeps a set of words, organized with one node for
    each letter. Each node has a branch for each letter that may follow it in the
    set of words.
    """
    def __init__(self):
        self.word = None
        self.children = {}

    def insert(self, word):
        node = self
        nodes_count = 0
        for letter in word:
            if letter not in node.children: 
                node.children[letter] = TrieNode()
                nodes_count += 1
            node = node.children[letter]
        node.word = word
        return nodes_count


class Trie:
    def __init__(self):
        self.node_count = 0
        self.word_count = 0
        self.root = TrieNode()

    def feed_words(self, words, sort=True):
        if sort:
            words.sort()
            
        for word in words:
            self.word_count += 1
            self.node_count += self.root.insert(word)


    def __unicode__(self):
        return u'Trie has %d words embeded into %d nodes' % (self.word_count, self.node_count)
    
    def __str__(self):
        return self.__unicode__().encode('utf-8')

    # The search function returns a list of all words that are less than the given
    # maximum distance from the target word
    def search(self, word, maxCost):
        # build first row
        currentRow = range(len(word) + 1)
    
        results = []
    
        # recursively search each branch of the trie
        for letter in self.root.children:
            self.searchRecursive(self.root.children[letter], letter, word, currentRow,
                results, maxCost)
    
        return results

    # This recursive helper is used by the search function above. It assumes that
    # the previousRow has been filled in already.
    def searchRecursive(self, node, letter, word, previousRow, results, maxCost):

        columns = len(word) + 1
        currentRow = [ previousRow[0] + 1 ]
    
        # Build one row for the letter, with a column for each letter in the target
        # word, plus one for the empty string at column 0
        for column in xrange(1, columns):
    
            insertCost = currentRow[column - 1] + 1
            deleteCost = previousRow[column] + 1
    
            if word[column - 1] != letter:
                replaceCost = previousRow[ column - 1 ] + 1
            else:                
                replaceCost = previousRow[ column - 1 ]
    
            currentRow.append(min(insertCost, deleteCost, replaceCost))
    
        # if the last entry in the row indicates the optimal cost is less than the
        # maximum cost, and there is a word in this trie node, then add it.
        if currentRow[-1] <= maxCost and node.word != None:
            results.append((node.word, currentRow[-1]))
    
        # if any entries in the row are less than the maximum cost, then 
        # recursively search each branch of the trie
        if min(currentRow) <= maxCost:
            for letter in node.children:
                self.searchRecursive(node.children[letter], letter, word, currentRow,
                    results, maxCost)


class DawgNode:
    """
    This class represents a node in the directed acyclic word graph (DAWG). It
    has a list of edges to other nodes. It has functions for testing whether it
    is equivalent to another node. Nodes are equivalent if they have identical
    edges, and each identical edge leads to identical states. The __hash__ and
    __eq__ functions allow it to be used as a key in a python dictionary.
    """
    NextId = 0
    
    def __init__(self):
        self.id = DawgNode.NextId
        DawgNode.NextId += 1
        self.final = False
        self.edges = {}

    def __str__(self):        
        arr = []
        if self.final: 
            arr.append("1")
        else:
            arr.append("0")

        for (label, node) in self.edges.iteritems():
            arr.append( label )
            arr.append( str( node.id ) )

        return "_".join(arr)

    def __hash__(self):
        return self.__str__().__hash__()

    def __eq__(self, other):
        return self.__str__() == other.__str__()

class Dawg:
    def __init__(self):
        self.previousWord = ""
        self.root = DawgNode()

        # Here is a list of nodes that have not been checked for duplication.
        self.uncheckedNodes = []

        # Here is a list of unique nodes that have been checked for
        # duplication.
        self.minimizedNodes = {}
        
        self.words_count = 0

    def insert( self, word ):
        if word < self.previousWord:
            raise Exception("Error: Words must be inserted in alphabetical order.")

        # find common prefix between word and previous word
        commonPrefix = 0
        for i in range( min( len( word ), len( self.previousWord ) ) ):
            if word[i] != self.previousWord[i]: break
            commonPrefix += 1

        # Check the uncheckedNodes for redundant nodes, proceeding from last
        # one down to the common prefix size. Then truncate the list at that
        # point.
        self._minimize( commonPrefix )

        # add the suffix, starting from the correct node mid-way through the
        # graph
        if len(self.uncheckedNodes) == 0:
            node = self.root
        else:
            node = self.uncheckedNodes[-1][2]

        for letter in word[commonPrefix:]:
            nextNode = DawgNode()
            node.edges[letter] = nextNode
            self.uncheckedNodes.append( (node, letter, nextNode) )
            node = nextNode

        node.final = True
        self.previousWord = word

    def finish( self ):
        # minimize all uncheckedNodes
        self._minimize( 0 );

    def _minimize( self, downTo ):
        # proceed from the leaf up to a certain point
        for i in range( len(self.uncheckedNodes) - 1, downTo - 1, -1 ):
            (parent, letter, child) = self.uncheckedNodes[i];
            if child in self.minimizedNodes:
                # replace the child with the previously encountered one
                parent.edges[letter] = self.minimizedNodes[child]
            else:
                # add the state to the minimized nodes.
                self.minimizedNodes[child] = child;
            self.uncheckedNodes.pop()

    def lookup( self, word ):
        node = self.root
        for letter in word:
            if letter not in node.edges: return False
            node = node.edges[letter]

        return node.final

    def nodeCount( self ):
        return len(self.minimizedNodes)

    def edgeCount( self ):
        count = 0
        for node in self.minimizedNodes:
            count += len(node.edges)
        return count
    
    def feed_words(self, words, sort=True):
        if sort:
            words.sort()
        for word in words:
            self.insert(word)
            self.words_count += 1
        self.finish()
        
    def __repr__(self):
        return 'dawg has %d words embeded into %d nodes and %d edges' % (self.words_count,
                self.nodeCount(), self.edgeCount())
        
    def size_of_dawg(self):
        """
        Unit bytes
        """
        return 4*self.edgeCount()

class EditDistanceBank():
    def __init__(self, words):
        self.words = words
        self.mapping_table = self._mapping_names(words)
        self.size = len(words)
        self.bank = np.zeros((self.size, self.size), dtype=np.int8)
        self.build_bank_thread = Thread(target=self._build_bank, name='Build editdistance bank')
        self.build_bank_thread.start()
    
    def get_max_distance(self):
        if self.build_bank_thread.is_alive():
            raise EditDistanceBank.InProgressError()
        return self.max_distance
        
    def _mapping_names(self, words):
        mapping = {}
        counter = 0
        for word in words:
            mapping[word] = counter
            counter += 1
        return mapping
    
    def _build_bank(self):
        max_value = 0
        for i in range(self.size - 1):
            for j in range(i + 1, self.size):
                if self.words[i] == '' and self.words[j] == '':
                    self.bank[i][j] = 1
                    self.bank[j][i] = 1
                else:
                    editdistance = levenshtein_dyn(self.words[i], self.words[j])
                    self.bank[i][j] = editdistance
                    self.bank[j][i] = editdistance
                    if max_value < editdistance:
                        max_value = editdistance
        self.max_distance = max_value
        return max_value

    def lookup(self, word1, word2):
        if self.build_bank_thread.is_alive():
            raise EditDistanceBank.InProgressError()
        idx1 = self.mapping_table[word1]
        idx2 = self.mapping_table[word2]
        return self.bank[idx1][idx2]
    
    def join(self):
        if self.build_bank_thread.is_alive():
            self.build_bank_thread.join()

    class InProgressError(Exception):
        def __init__(self):
            pass
            
        def __repr__(self):
            return 'Building edit distance bank in progress, please wait'