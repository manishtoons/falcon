# relation_syntax = 'sg_asset_type:sg_assetgroup.name:code'
hierarchy_seperator = ':'
nesting_seperator = '.'


def build_relations(asset_dict, relation_syntax):
   """
   This very method is the soul of the tool, this will create a giant 
   way to mimic parent-child relations in a node base environment, but
   dictionary, where all the relations will get build, now this is a
   the approach you would find in this method wont be ideal, it got 
   created in no time, with not much of thought process and brainstorming

   :Usage:

       we gonna create hierarchy syntax here, which will be used in builing up 
       relations and it would work out of the box.
       it will get split by ':' and any '.' found in considered as nested query
       in guven dictionary, child objects will be returned as always.
       in this following example -

       relation_syntax = 'sg_asset_type:sg_assetgroup.name:code'
       sg_asset_type         - is root of all relation
       sg_assetgroup.name    - is child of sg_asset_type
       code                  - is child of sg_asset_type
       sg_asset_type_
                     |
                     sg_assetgroup.name
                                        |
                                         code

   """
   relations = list()

   hierarchy_list = relation_syntax.split(':')

   # we gonna do some bullshit crap here, to align this dic inline
   for each_entry in asset_dict:
       level_nodes = list()

       for index, each_level in enumerate(hierarchy_list):
           children = list()

           parent_dict = dict()
           if '.' in each_level:
               level_split = each_level.split('.')
               parent_key = 'each_entry' 
               parent_key += "['"
               parent_key += "']['".join(level_split[:-1])
               parent_key += "']"
               parent_dict = eval(parent_key)

               key_string = 'each_entry'
               key_string += "['"
               key_string += "']['".join(level_split)
               key_string += "']"
               node_name = eval(key_string)

               # key_element to sort dic
               key_element = key_string.replace('each_entry', '')

               # get the children
               # if index != (len(hierarchy_list) - 1):
               sorted_input = sorted(asset_dict, key=lambda k: eval('k%s' % key_element))
               for each_input in sorted_input:
                   if eval('each_input%s' % key_element) == node_name:
                       children.append(each_input)
                   elif children:
                       break
           else:
               node_name = each_entry[each_level]

               for node_attr in each_entry:
                   if isinstance(node_attr, dict):
                       continue
                   parent_dict.update({'%s' % node_attr: each_entry[node_attr]})

               # get the children for non-nested element
               sorted_input = sorted(asset_dict, key=lambda k: each_entry[each_level])
               for each_input in sorted_input:
                   if each_input[each_level] == node_name:
                       children.append(each_input)
                   elif children:
                       break

           # we would want to have one common attribute in out Node object
           # so, we will have name attribute, where it stores value of each
           # key given in relation syntax
           node_spec = dict(
                               name=node_name,
                           )

           # override any parent information
           # as we would be creating 'name' key, make sure, any existing key
           # from parent_dict wont override it
           if parent_dict:
               node_spec.update(parent_dict)

           # safer side override name
           node_spec['name'] = node_name

           level_node = Node(spec=node_spec,
                             children=children,
                             parent=None if index==0 else level_nodes[index-1],
                             relation_syntax=relation_syntax,
                             identifier=each_level
                             )            
           level_nodes.append(level_node)

       yield level_nodes[-1]


class NodeEngineException(Exception):
    pass


# 'relation_syntax' = 'sg_asset_type:sg_assetgroup.name:code:' 
#                     'steps.short_name:short.task.entity.name'

def tree(node_spec_item_list, relation_syntax, reverse=False):
    """
    Returns generator `Node` object.
    
    :param node_spec_item_list: list of dicts
    :param relation_syntax: string of keys which defines hierarchy in node_spec_item_list
    :param reverse: True if want to rever the realtions
    """
    hierarchy_keys = relation_syntax.split(hierarchy_seperator)

    if reverse:
       hierarchy_keys.sort(reverse=True) 

    # loop through all the spec items
    for each_item in node_spec_item_list:
        # check if its a dict, if not kick back
        if not isinstance(each_item, dict):
            raise NodeEngineException('Required list of dict '
                                      'found type %s' % type(each_item))

        # now loop through key if hierarchy_keys and evaluate the relation
        for each_level in hierarchy_keys:
            # check if each_level item requires netsting
            if __is_nested_key(each_level):
                # resolve the nesting here
                # check if, levels in keys are part of any list
                pass


def __resolve_keys(hierarchy_level, spec_item):
    # check if any of key from the hierarchy_level, is list item
    # if yes, then we need to loop through it
    all_levels = hierarchy_level.split(nesting_seperator)

    # create a var, which holds, the nature of each level,
    # means, type of index
    level_nature = dict()

    # loop through all levels
    for level_index, each_level in enumerate(all_levels):
        # print 'checking with -', each_level
        is_list = False
        parent_is_list = False

        # check if we have a list as level's value
        if level_index == 0:
            level_value = spec_item[each_level]
        else:
            # we need to iterate thorugh this list of out previous index
            # item is actually a list type
            if isinstance(level_nature[level_index - 1], list):
                parent_is_list = True

            level_full_path = "['" 
            level_full_path += "']['".join(all_levels[:(level_index+1)])
            level_full_path += "']"
            print level_full_path
            level_value = spec_item[eval(level_full_path)]

        if isinstance(level_value, list):
            print 'level -', each_level, 'is a list input'
            is_list = True 

        level_nature[level_index] = type(level_value)

def __get_spec_from_nesting():
    pass


def __is_nested_key(level_key):
    return nesting_seperator in level_key
    

class Node(object):

   def __init__(self, spec, parent,children=[], 
               relation_syntax='', identifier=''):
       super(Node, self).__init__()

       self._spec = spec
       self.parent = parent
       self._children_spec = children
       self._relation_syntax = relation_syntax
       self._chilren_items = []
       self._identifier = identifier
       self._root = None
       self._all_descendants = []
       self._all_parents  = []

       # we gonna create class attribute out of self._spec
       self._create_class_attributes(self._spec)
       self.__id__ = '%0x08x' % id(self)

   def _create_class_attributes(self, dict_object):
       for each_key in dict_object:
           if each_key.startswith('_'):
               continue
           # setattr(self, each_key, dict_object[each_key])
           self.__dict__[each_key] = dict_object[each_key]

   @property
   def identifier(self):
       return self.__getattr__('_identifier')

   @property
   def children(self):
       if self._chilren_items:
           return self._chilren_items

       if not isinstance(self._chilren_items, list):
           return []

       chilren_items = list(build_relations(self._children_spec, self._relation_syntax))
       if chilren_items and len(chilren_items) == 1 and self._spec == chilren_items[0]._spec:
           self._chilren_items = None
           return None

       self._chilren_items = chilren_items[:]
       return self._chilren_items

   def get_children(self, level=1):
       """Method returns children nodes of the current parent node"""
       # get children
       if not self._chilren_items:
           self.children()

       # now get them
       all_children = []
       # XXX implement this

       return all_children

   @property
   def root(self):
       """Returns root object"""

       if self._root:
           return self.__getattr__('_root')

       if not self.parent:
           return

       self._all_parents.append(self.parent)

       # lets go recursive        
       current_parent = self.parent
       while current_parent:
           if not current_parent.parent:
               break
           else:
               current_parent = current_parent.parent
               self._all_parents.append(current_parent)

       self._root = current_parent

       return self.__getattr__('_root')

   @property
   def all_parents(self):
       # get root
       self.root

       return self.__getattr__('_all_parents')

   def __getattr__(self, key):
       if key in self._spec:
           return self._spec[key]
       elif key in self.__dict__:
           return self.__dict__[key]

       raise AttributeError('Node object has no attribute name %s' % key)

   def __setattr__(self, key, value):
       if '_spec' in self.__dict__ and key in self._spec.keys():
           self._spec[key] = value
       else:
           self.__dict__[key] = value

   def __repr__(self):
       msg = self.__read__()
       if 'type' in msg:
           msg.remove('type')
       return '<%s.%s: \n%s\n%s object@%s>' % (self.__module__, 
                                      self.__class__.__name__, 
                                     '\n'.join(msg),
                                     self.__dict__.get('type', ''),
                                     self.__id__)

   def __str__(self):
       return ', '.join(self.__read__())

   def __read__(self):
       msg = []
       for each_spec in self._spec:
           msg.append('%s: %s' % (each_spec, self._spec[each_spec]))

       if self.parent:
           msg.append('Parent: <%s.%s %s object@%s >' % (self.__module__,
                                                        self.__class__.__name__,
                                                        self.parent.name,
                                                        self.parent.__id__))
       else:
           msg.append('Parent: None')
       if self.children:
           msg.append('Children: %s' % len(self.children))
       else:
           msg.append('Children: 0')
       msg.append('identifier: %s' % self._identifier)
       return msg

