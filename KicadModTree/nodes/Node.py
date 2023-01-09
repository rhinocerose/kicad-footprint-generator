# KicadModTree is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# KicadModTree is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kicad-footprint-generator. If not, see < http://www.gnu.org/licenses/ >.
#
# (C) 2016 by Thomas Pointhuber, <thomas.pointhuber@gmx.at>
# modifications 2022 by Armin Schoisswohl (@armin.sch)
import math
from copy import copy, deepcopy

from KicadModTree.Vector import *


class MultipleParentsError(RuntimeError):
    def __init__(self, message):

        # Call the base class constructor with the parameters it needs
        super(MultipleParentsError, self).__init__(message)


class RecursionDetectedError(RuntimeError):
    def __init__(self, message):

        # Call the base class constructor with the parameters it needs
        super(RecursionDetectedError, self).__init__(message)


class VirtualNodeError(RuntimeError):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(VirtualNodeError, self).__init__(message)


class Node(object):
    def __init__(self):
        self._parent = None
        self._childs = []

    def __iter__(self):
        return self.allChildItems()

    def __len__(self):
        return len(self.getNormalChilds()) + len(self.getVirtualChilds())

    def append(self, node):
        '''
        add node to child
        '''
        if not isinstance(node, Node):
            raise TypeError('invalid object, has to be based on Node')

        if node._parent:
            raise MultipleParentsError('muliple parents are not allowed!')

        self._childs.append(node)

        node._parent = self

    def extend(self, nodes):
        '''
        add list of nodes to child
        '''
        new_nodes = []
        for node in nodes:
            if not isinstance(node, Node):
                raise TypeError('invalid object, has to be based on Node')

            if node._parent or node in new_nodes:
                raise MultipleParentsError('muliple parents are not allowed!')

            new_nodes.append(node)

        # when all went smooth by now, we can set the parent nodes to ourself
        for node in new_nodes:
            node._parent = self

        self._childs.extend(new_nodes)

    @staticmethod
    def _removeNode(*, parent, node, virtual: bool = False):
        '''
        remove child from node
        '''
        if not isinstance(node, Node):
            raise TypeError('invalid object, has to be based on Node')

        removed = False

        while node in parent.getNormalChilds():
            parent.getNormalChilds().remove(node)
            removed = True

        if virtual:
            while node in parent.getVirtualChilds():
                parent.getVirtualChilds().remove(node)
                removed = True

        if (removed):
            node._parent = None

    def remove(self, node, traverse: bool = False, virtual: bool = False):
        '''
        remove child from node or from the tree
        '''
        if not isinstance(node, Node):
            raise TypeError('invalid object, has to be based on Node')

        if not virtual and node in self.getVirtualChilds():
            raise VirtualNodeError('the node you are trying to remove is virtual')

        if (not traverse):
            self._removeNode(parent=self, node=node, virtual=virtual)
        else:
            if (node == self):
                if (node._parent):
                    self._removeNode(parent=node._parent, node=node, virtual=virtual)
            else:
                for child in self.allChildItems() if virtual else self.normalChildItems():
                    child.remove(node, traverse=traverse, virtual=virtual)

    def insert(self, node):
        '''
        moving all childs into the node, and using the node as new parent of those childs
        '''
        if not isinstance(node, Node):
            raise TypeError('invalid object, has to be based on Node')

        for child in copy(self._childs):
            self.remove(child)
            node.append(child)

        self.append(node)

    def copy(self):
        copy = deepcopy(self)
        copy._parent = None
        return copy

    def serialize(self):
        nodes = [self]
        for child in self.getAllChilds():
            nodes += child.serialize()
        return nodes

    def getNormalChilds(self):
        '''
        Get all normal childs of this node
        '''
        return self._childs

    def normalChildItems(self):
        return iter(self.getNormalChilds())

    def getVirtualChilds(self):
        '''
        Get virtual childs of this node
        '''
        return []

    def virtualChildItems(self):
        """
        virtual child iterator
        """
        return iter(self.getVirtualChilds())

    def getAllChilds(self):
        '''
        Get virtual and normal childs of this node
        '''
        return self.getNormalChilds() + self.getVirtualChilds()

    def allChildItems(self):
        for c in self.normalChildItems():
            yield c
        for c in self.virtualChildItems():
            yield c

    @property
    def num_virtual_nodes(self):
        return len(self.getVirtualChilds())

    @property
    def num_normal_nodes(self):
        return len(self.getNormalChilds())

    @property
    def num_all_nodes(self):
        return self.num_virtual_nodes + self.num_normal_nodes

    def getParent(self):
        '''
        get Parent Node of this Node
        '''
        return self._parent

    def getRootNode(self):
        '''
        get Root Node of this Node
        '''

        # TODO: recursion detection
        if not self.getParent():
            return self

        return self.getParent().getRootNode()

    def getRealPosition(self, coordinate, rotation=None):
        '''
        return position of point after applying all transformation and rotation operations
        '''
        if not self._parent:
            if rotation is None:
                # TODO: most of the points are 2D Nodes
                return Vector3D(coordinate)
            else:
                return Vector3D(coordinate), rotation

        return self._parent.getRealPosition(coordinate, rotation)

    def calculateBoundingBox(self, outline=None):
        min_x, min_y = math.inf, math.inf
        max_x, max_y = -math.inf, -math.inf

        if outline:
            min_x = outline['min']['x']
            min_y = outline['min']['y']
            max_x = outline['max']['x']
            max_y = outline['max']['y']

        for child in self.getAllChilds():
            child_outline = child.calculateBoundingBox()

            min_x = min([min_x, child_outline['min']['x']])
            min_y = min([min_y, child_outline['min']['y']])
            max_x = max([max_x, child_outline['max']['x']])
            max_y = max([max_y, child_outline['max']['y']])

        return {'min': Vector2D(min_x, min_y), 'max': Vector2D(max_x, max_y)}

    def _getRenderTreeText(self):
        '''
        Text which is displayed when generating a render tree
        '''
        return type(self).__name__

    def _getRenderTreeSymbol(self):
        '''
        Symbol which is displayed when generating a render tree
        '''
        if self._parent is None:
            return "+"

        return "*"

    def getRenderTree(self, rendered_nodes=None):
        '''
        print render tree
        '''
        if rendered_nodes is None:
            rendered_nodes = set()

        if self in rendered_nodes:
            raise RecursionDetectedError('recursive definition of render tree!')

        rendered_nodes.add(self)

        tree_str = "{0} {1}".format(self._getRenderTreeSymbol(), self._getRenderTreeText())
        for child in self.getNormalChilds():
            tree_str += '\n  '
            tree_str += '  '.join(child.getRenderTree(rendered_nodes).splitlines(True))

        return tree_str

    def getCompleteRenderTree(self, rendered_nodes=None):
        '''
        print virtual render tree
        '''
        if rendered_nodes is None:
            rendered_nodes = set()

        if self in rendered_nodes:
            raise RecursionDetectedError('recursive definition of render tree!')

        rendered_nodes.add(self)

        tree_str = "{0} {1}".format(self._getRenderTreeSymbol(), self._getRenderTreeText())
        for child in self.getAllChilds():
            tree_str += '\n  '
            tree_str += '  '.join(child.getCompleteRenderTree(rendered_nodes).splitlines(True))

        return tree_str
