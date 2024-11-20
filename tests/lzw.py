
import os
from typing import Tuple
import struct

import time
import tracemalloc
import json
import argparse
import json
import sys



class CompactTrieNode:
  def __init__(self, binary_string: str = "", value: str = "", is_leaf: bool = False) -> None:
    self.children = [None, None]
    self.is_leaf = is_leaf
    self.binary_string = binary_string
    self.value = value
    self.unique_id = id(self)  # Temporário

class CompactTrie:
  def __init__(self) -> None:
    self.root = None

  def get_common_prefix_length(self, key1: str, key2: str) -> int:
    i = 0
    while i < min(len(key1), len(key2)) and key1[i] == key2[i]:
        i += 1
    return i

  def search(self, key: str) -> CompactTrieNode:
    current_node = self.root

    if(current_node == None):
      return None

    while True:
      if((current_node.binary_string == key) and (current_node.is_leaf == True)):
        return current_node

      common_prefix_length = self.get_common_prefix_length(current_node.binary_string, key)

      if(common_prefix_length == len(current_node.binary_string)):

        key = key[common_prefix_length:]

        if current_node.children[int(key[0])] == None:
          return None

        current_node = current_node.children[int(key[0])]
      else:
        return None

  def insert(self, key: str, value: str) -> None:
    # Caso em que não tínhamos raiz
    if(self.root == None):
      self.root = CompactTrieNode(key, value, True)
      return

    else:
      current_node = self.root

      while True:
        # Achei, posso parar
        if(current_node.binary_string == key):
          current_node.is_leaf = True
          return

        common_prefix_length = self.get_common_prefix_length(current_node.binary_string, key)

        # Sobrou parte da key ainda, com certeza
        if (common_prefix_length == len(current_node.binary_string)):
          key = key[common_prefix_length:]

          if current_node.children[int(key[0])] == None:
            current_node.children[int(key[0])] = CompactTrieNode(key, value, True)
            return

          current_node = current_node.children[int(key[0])]

        # Achei onde vou ter que criar novo nó para inserir
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

  # Temporário
  def visualize(self, filename="compact_trie"):
      dot = Digraph(comment="Compact Trie")

      def add_nodes_edges(node, parent_label=None):
          if node is None:
              return

          new_node_binary_string = node.binary_string
          new_node_binary_string = new_node_binary_string.replace("0", "a")
          new_node_binary_string = new_node_binary_string.replace("1", "b")

          node_label = f"{new_node_binary_string}_{node.unique_id}"

          display_label = f"{new_node_binary_string}"
          if(node.is_leaf):
            display_label  += f"\\nValue: {node.value}"

          dot.node(node_label, display_label, shape='circle', color='black', fontcolor='red' if node.is_leaf else 'blue')

          if parent_label:
              dot.edge(parent_label, node_label)
          if node.children[0] is not None:
              add_nodes_edges(node.children[0], node_label)
          if node.children[1] is not None:
              add_nodes_edges(node.children[1], node_label)

      if self.root is not None:
          add_nodes_edges(self.root)

      dot.render(filename, format="png", cleanup=True)
      print(f"Compact trie saved as {filename}.png")

# Para debug
def binary_to_chars(binary_string):
    # Ensure the binary string length is a multiple of 8 (since each character is 8 bits)
    if len(binary_string) % 8 != 0:
        raise ValueError("Binary string length must be a multiple of 8.")

    # Split the binary string into chunks of 8 bits
    chars = [binary_string[i:i+8] for i in range(0, len(binary_string), 8)]

    # Convert each 8-bit binary chunk to its corresponding character
    result = ''.join(chr(int(char, 2)) for char in chars)

    return result

# # Função para converter um conjunto de bytes em um '.txt'
# def write_txt_file(decoded_bytes, output_file):
#     decoded_string = ''.join([chr(byte) for byte in decoded_bytes])
#     with open(output_file, 'w', encoding='utf-8') as file:
#         file.write(decoded_string)

def write_txt_file(decoded_bytes, output_file):
    with open(output_file, 'wb') as file:
        file.write(bytes(decoded_bytes))


# Função para converter um conjunto de bytes em um '.bmp' ou '.pgm'
def write_image_file(decoded_bytes, output_file):
    with open(output_file, 'wb') as file:
        file.write(bytes(decoded_bytes))

def write_audio_file(decoded_bytes, output_file):
    with open(output_file, 'wb') as file:
        file.write(bytes(decoded_bytes))

# Função para remover zeros à esquerda em uma string binárias
def remove_leading_zeros(binary_str):
  return binary_str.lstrip('0') or '0'


class TrieLZW:
  # Atributos para armazenar as estatísticas
  def __init__(self):
      self.stats = {
          'compression_ratio_over_time': [],
          'dictionary_size_over_time': [],
          'execution_time': 0,
          'memory_usage': 0
      }

  # Realiza a compressão LZW do arquivo passado como parâmetro
  def compress(self, file_path: str="") -> Tuple[str, str]:

    # Iniciar rastreamento de tempo e memória
    start_time = time.time()
    tracemalloc.start()

    # Utilizando a Trie Compacta Binária como dicionário no algoritmo
    dictionary = CompactTrie()

    # Inicializando todas as chaves de 00000000 até 11111111 no dicionário, com respectivos valores sendo a própria chave
    for num in range(256):
      byte_num = format(num, '08b')
      dictionary.insert(byte_num, byte_num)

    dict_size = 256 # O dicionário começa com todos os símbolos ASCII
    num_bits_values = 9 # Começaremos usando 9 bits para representar códigos a partir de agora
    next_dict_size_limit = 2 * 256 # Os 9 bits serão suficientes para representar códigos de 000000000 (0) até 111111111 (511)

    # Inicializando variáveis utilizadas pela compressão LZW
    string = ""
    compressed_data = []

    # Aplicando a compressão LZW, considerando cada byte do arquivo orignal como um símbolo de entrada
    try:
      count = 256
      with open(file_path, "rb") as file:
        while (byte := file.read(1)):
          symbol = bin(int.from_bytes(byte, "big"))[2:].zfill(8)

          string_plus_symbol = string + symbol

          if dictionary.search(string_plus_symbol) != None:
              string = string_plus_symbol
          else:
            # Caso em que o dicionário tem tamanho dinâmico
            if(dict_size == next_dict_size_limit):
                num_bits_values += 1
                next_dict_size_limit *= 2

            current_string_formatted_binary_value = dictionary.search(string).value.zfill(num_bits_values)
            compressed_data.append(current_string_formatted_binary_value)
            new_key_value = bin(dict_size)[2:].zfill(num_bits_values)
            dictionary.insert(string_plus_symbol, new_key_value)
            dict_size += 1
            string = symbol


            # Atualizar estatísticas
            self.stats['dictionary_size_over_time'].append(dict_size)

            # Calcular o tamanho comprimido atual (em bits)
            compressed_size_bits = sum(len(code) for code in compressed_data)

            # Calcular o tamanho original processado até agora (em bits)
            original_size_bits = (len(compressed_data) + 1) * 8  # Cada símbolo original tem 8 bits

            # Calcular a taxa de compressão atual
            compression_ratio = compressed_size_bits / original_size_bits
            self.stats['compression_ratio_over_time'].append(compression_ratio)


        if(dictionary.search(string) != None):
          current_string_formatted_binary_value = dictionary.search(string).value.zfill(num_bits_values)
          compressed_data.append(current_string_formatted_binary_value)

    # Tratando erros que podem ocorrer na abertura de um arquivo
    except FileNotFoundError as e:
      print(f"Arquivo não encontrado -> {e}")
    except IOError as e:
      print(f"Erro de I/O -> {e}")
    except Exception as e:
      print(f"Um erro ocorreu: {e}")

    # Salvando o nome do arquivo original e sua extensão para que o arquivo de compressão possa ser salvo
    base_file_name = os.path.basename(file_path)
    file_name_without_ext, file_extension = os.path.splitext(base_file_name)

    # Nome do arquivo comprimido
    compressed_file_name = f"compressed_{file_name_without_ext}.bin"
    file_name = file_name_without_ext  # Add this line
    # # Salvando o nome do arquivo original e sua extensão para que o arquivo de compressão possa ser salvo
    # file_name, file_extension = os.path.splitext(file_path)

    with open(f"compressed_{file_name}.bin", "wb") as file:
      # Convertendo os códigos para uma única string
      final_concat_string_data = ''.join(compressed_data)

      # Verificando se algum padding deverá ser adicionado para que tenhamos um número inteiro de bytes no arquivo comprimido
      padding_size = (8 - len(final_concat_string_data) % 8) % 8
      final_concat_string_data = '0' * padding_size + final_concat_string_data

      # Adicionando uma flag, no arquivo comprimido, para representar o tamanho do padding que foi adicionado
      file.write(bytes([padding_size]))

      # Convertendo a string de dados comprimidos para bytes e escrevendo no arquivo comprimido final
      bits = []
      for char in final_concat_string_data:
        bits.append(1 if char == '1' else 0)
      byte = 0
      bit_count = 0
      for bit in bits:
        byte = (byte << 1) | bit
        bit_count += 1
        if bit_count == 8:
          file.write(bytes([byte]))
          byte = 0
          bit_count = 0

      # Finalizar rastreamento de tempo e memória
      end_time = time.time()
      self.stats['execution_time'] = end_time - start_time

      current_memory, peak_memory = tracemalloc.get_traced_memory()
      self.stats['memory_usage'] = peak_memory / 1024  # Converter para KB
      tracemalloc.stop()

      return [file_name_without_ext, file_extension]
  
  # Realiza a descompressão LZW do arquivo passado como parâmetro
  def decompress(self, file_path: str="", original_file_name: str="", original_file_extension: str="") -> None:

    # Iniciar rastreamento de tempo e memória
    start_time = time.time()
    tracemalloc.start()

    # Utilizando a Trie Compacta Binária como dicionário no algoritmo
    dictionary = CompactTrie()

    # Inicializando todas as chaves de 0, 1, 10, 11, 100, ... até 11111111 no dicionário (sem padding), com respectivos valores sendo a própria chave (com padding)
    for num in range(256):
      numeric_key = bin(num)[2:]
      numeric_key_8bit_value = format(num, '08b')
      dictionary.insert(numeric_key, numeric_key_8bit_value)

    dict_size = 256 # O dicionário começa com todos os número de 0 até 255, cada um representando um símbolo ASCII
    decompression_size = 9 # Começaremos puxando 9 bits do arquivo comprimido por vez
    next_size_limit = 2 * 256 # Os 9 bits serão suficientes até que o tamanho do dicionário atinja 512 elementos

    # Abrindo o arquivo já comprimido e convertendo seus bytes em uma única string
    compressed_data = ""
    try:
      with open(file_path, "rb") as file:
        file_data = file.read()
        compressed_data = ''.join(format(byte, '08b') for byte in file_data)
    # Tratando erros que podem ocorrer na abertura de um arquivo
    except FileNotFoundError:
      print(f"File not found: {file_path}")
    except IOError as e:
      print(f"Error reading the file: {e}")
    except Exception as e:
      print(f"An unexpected error occurred: {e}")

    # Retirando os bits de padding do arquivo comprimido
    padding_size = int(compressed_data[:8], 2)
    compressed_data = compressed_data[(8 + padding_size):]

    # Inicializando as variáveis que serão empregadas posteriormente
    string = compressed_data[:decompression_size]
    string = string[-8:]

    compressed_data = compressed_data[decompression_size:]
    decompressed_data = [string]

    # Aplicando a descompressão LZW
    while(len(compressed_data) > 0):
        # Caso em que o dicionário tem tamanho dinâmico
        if(dict_size == next_size_limit - 1):
          decompression_size += 1
          next_size_limit *= 2

        k = compressed_data[:decompression_size]
        compressed_data = compressed_data[decompression_size:]

        k = remove_leading_zeros(k)

        if dictionary.search(k) != None:
          entry = dictionary.search(k).value
        else:
          new_value_entry_concat = string[:8]
          entry = string + new_value_entry_concat

        decompressed_data.append(entry)
        new_key = bin(dict_size)[2:] if dict_size != 0 else '0'
        dictionary.insert(new_key, string + entry[:8])
        dict_size += 1

        string = entry

    decompressed_concat_string = ''.join(decompressed_data)

    # Checando algum possível erro que possa ter ocorrido na descompressão (o tamanho do arquivo final deve ser um múltiplo de 8)
    if len(decompressed_concat_string) % 8 != 0:
      raise ValueError("O arquivo descomprimido não tem um número inteiro de bytes!")

    # Transformando a string binárias em bytes individuais
    byte_chunks = [decompressed_concat_string[i:i+8] for i in range(0, len(decompressed_concat_string), 8)]
    bytes_ = [int(chunk, 2) for chunk in byte_chunks]

    # Convert integers to their ASCII characters
    ascii_characters = [chr(i) for i in bytes_]
    # Join characters into a string (optional)
    ascii_string = ''.join(ascii_characters)


    # Nome do arquivo descomprimido
    decompressed_file_name = f"decompressed_{original_file_name}{original_file_extension}"



    # Gerando o arquivo inicial
    switch = {
        '.txt': write_txt_file,
        '.bmp': write_image_file,
        '.bin': write_image_file,
        '.wav': write_audio_file,
        '.pgm': write_image_file,

    }
    handler = switch.get(original_file_extension)
    if handler:
        handler(bytes_, decompressed_file_name)
    else:
        print("Unsupported file type.")


    # Finalizar rastreamento de tempo e memória
    end_time = time.time()
    self.stats['execution_time'] = end_time - start_time

    current_memory, peak_memory = tracemalloc.get_traced_memory()
    self.stats['memory_usage'] = peak_memory / 1024  # Converter para KB
    tracemalloc.stop()







def main():
    parser = argparse.ArgumentParser(description='Compress or decompress files using LZW algorithm with Compact Trie.')
    subparsers = parser.add_subparsers(dest='command', help='Available commands: compress, decompress')

    # Parser for the 'compress' command
    compress_parser = subparsers.add_parser('compress', help='Compress a file')
    compress_parser.add_argument('input_file', type=str, help='Path to the input file to compress')
    compress_parser.add_argument('output_file', type=str, help='Path to the output compressed file')
    compress_parser.add_argument('--max-bits', type=int, help='Maximum number of bits (default: 12)', default=12)
    compress_parser.add_argument('--stats-file', type=str, help='Path to save compression stats', default=None)

    # Parser for the 'decompress' command
    decompress_parser = subparsers.add_parser('decompress', help='Decompress a file')
    decompress_parser.add_argument('input_file', type=str, help='Path to the input compressed file')
    decompress_parser.add_argument('output_file', type=str, help='Path to the output decompressed file')
    decompress_parser.add_argument('--max-bits', type=int, help='Maximum number of bits (default: 12)', default=12)
    decompress_parser.add_argument('--stats-file', type=str, help='Path to save decompression stats', default=None)

    args = parser.parse_args()

    if args.command == 'compress':
        compress(args.input_file, args.output_file, args.stats_file, args.max_bits)
    elif args.command == 'decompress':
        decompress(args.input_file, args.output_file, args.stats_file, args.max_bits)
    else:
        parser.print_help()

def compress(input_file, output_file, stats_file=None, max_bits=12):
    trie_lzw = TrieLZW()

    # Executa a compressão
    trie_lzw.compress(input_file)

    # Obter o nome base do arquivo de entrada
    input_base_name = os.path.splitext(os.path.basename(input_file))[0]
    compressed_file_name = f"compressed_{input_base_name}.bin"

    if os.path.exists(compressed_file_name):
        os.rename(compressed_file_name, output_file)
    else:
        print(f"Error: Compressed file {compressed_file_name} not found.")
        sys.exit(1)

    # Salva as estatísticas, se especificado
    if stats_file:
        with open(stats_file, 'w') as f:
            json.dump(trie_lzw.stats, f, indent=4)
        print(f"Compression stats saved to {stats_file}")

    print(f"Compression completed: {output_file}")
    
def decompress(input_file, output_file, stats_file=None, max_bits=12):
    trie_lzw = TrieLZW()

    # Obter o nome base e extensão do arquivo de saída
    output_base_name, output_extension = os.path.splitext(os.path.basename(output_file))
    original_file_name = output_base_name.replace('decompressed_', '')

    # Executa a descompressão
    trie_lzw.decompress(input_file, original_file_name, output_extension)

    # Nome do arquivo descomprimido gerado pelo método
    decompressed_file_name = f"decompressed_{original_file_name}{output_extension}"

    if os.path.exists(decompressed_file_name):
        os.rename(decompressed_file_name, output_file)
    else:
        print(f"Error: Decompressed file {decompressed_file_name} not found.")
        sys.exit(1)

    # Salva as estatísticas, se especificado
    if stats_file:
        with open(stats_file, 'w') as f:
            json.dump(trie_lzw.stats, f, indent=4)
        print(f"Decompression stats saved to {stats_file}")

    print(f"Decompression completed: {output_file}")

if __name__ == '__main__':
    main()
