# Classe que implementa os nós da Trie
class CompactTrieNode:
  def __init__(self, binary_string: str = "", value: str = "", is_leaf: bool = False) -> None:
    self.children = [None, None]
    self.is_leaf = is_leaf
    self.binary_string = binary_string
    self.value = value

# Classe que implementa uma Trie a qual opera sobre strings binárias
class CompactTrie:
  def __init__(self) -> None:
    self.root = None

  # Função auxilixar para buscar prefixos
  def get_common_prefix_length(self, key1: str, key2: str) -> int:
    i = 0
    while i < min(len(key1), len(key2)) and key1[i] == key2[i]:
        i += 1
    return i
 
  # Busca por uma chave na trie
  def search(self, key: str) -> CompactTrieNode:
    current_node = self.root

    if(current_node == None):
      return None

    while True:

      if(current_node.binary_string == key):
        if(current_node.is_leaf == True):
          return current_node
        else:
          return None

      common_prefix_length = self.get_common_prefix_length(current_node.binary_string, key)

      if(common_prefix_length == len(current_node.binary_string)):

        key = key[common_prefix_length:]

        if current_node.children[int(key[0])] == None:
          return None

        current_node = current_node.children[int(key[0])]
      else:
        return None
  
  # Insere uma chave na árvore
  def insert(self, key: str, value: str) -> None:
    if(self.root == None):
      self.root = CompactTrieNode(key, value, True)
      return

    else:
      current_node = self.root

      while True:
        if(current_node.binary_string == key):
          current_node.is_leaf = True
          return

        common_prefix_length = self.get_common_prefix_length(current_node.binary_string, key)

        if (common_prefix_length == len(current_node.binary_string)):
          key = key[common_prefix_length:]

          if current_node.children[int(key[0])] == None:
            current_node.children[int(key[0])] = CompactTrieNode(key, value, True)
            return

          current_node = current_node.children[int(key[0])]

        else:
          key = key[common_prefix_length:]

          if(current_node.is_leaf == True):
            old_suffix_node = CompactTrieNode(current_node.binary_string[common_prefix_length:], current_node.value, True)
          else:
            old_suffix_node = CompactTrieNode(current_node.binary_string[common_prefix_length:], current_node.value)

          old_suffix_node.children[0] = current_node.children[0]
          old_suffix_node.children[1] = current_node.children[1]

          current_node.binary_string = current_node.binary_string[:common_prefix_length]

          if(len(key) > 0):
            key_suffix_node = CompactTrieNode(key, value, True)
            current_node.is_leaf = False
            current_node.children[int(key_suffix_node.binary_string[0])] = key_suffix_node
            current_node.children[int(old_suffix_node.binary_string[0])] = old_suffix_node
          else:
            current_node.value = value
            current_node.is_leaf = True
            current_node.children = [None, None]
            current_node.children[int(old_suffix_node.binary_string[0])] = old_suffix_node
          return

  # Deleta uma chave da trie, caso ela exista
  def delete_key(self, key: str) -> None:
    if(self.search(key) == None):
      return

    current_node = self.root
    last_node = self.root

    if(current_node.binary_string == key):
      if(current_node.children[0] == None and current_node.children[1] == None):
        self.root = None
        return
      elif(current_node.children[0] != None and current_node.children[1] != None):
        current_node.is_leaf = False
        return
      else:
        valid_child = 0 if current_node.children[0] != None else 1
        current_node.children[valid_child].binary_string = current_node.binary_string + current_node.children[valid_child].binary_string
        self.root = current_node.children[valid_child]
        return

    while True:
      if((current_node.binary_string == key) and (current_node.is_leaf == True)):
        if((current_node.children[0] != None) and (current_node.children[1] != None)):
          current_node.is_leaf = False
        elif((current_node.children[0] == None) and (current_node.children[1] == None)):
          last_node.children[int(current_node.binary_string[0])] = None

          if(last_node.is_leaf == False):
            last_node_other_child = 0 if current_node.binary_string[0] == '1' else 1

            if(last_node.children[last_node_other_child] != None):
              last_node.binary_string += last_node.children[last_node_other_child].binary_string
              last_node.value = last_node.children[last_node_other_child].value
              if(last_node.children[last_node_other_child].is_leaf):
                last_node.is_leaf = True
              last_node.children = last_node.children[last_node_other_child].children
        else:
          valid_child = 0 if current_node.children[0] != None else 1
          current_node.children[valid_child].binary_string = current_node.binary_string + current_node.children[valid_child].binary_string
          last_node.children[int(current_node.children[valid_child].binary_string[0])] = current_node.children[valid_child]
        return

      common_prefix_length = self.get_common_prefix_length(current_node.binary_string, key)
      key = key[common_prefix_length:]
      last_node = current_node
      current_node = current_node.children[int(key[0])]