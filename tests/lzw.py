
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


import subprocess
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import filecmp

# Configurações para melhor visualização dos gráficos
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (18, 12)  # Aumenta o tamanho padrão das figuras

# Diretório onde os arquivos de teste estão localizados
test_dir = 'test_files'

# Verifica se o diretório 'tests' existe
if not os.path.exists(test_dir):
    print(f"O diretório '{test_dir}' não existe. Por favor, certifique-se de que os arquivos de teste estão na pasta '{test_dir}'.")
    exit(1)

# Lista para armazenar os arquivos que precisam ser processados
files_to_process = []

# Extensões de arquivos a serem considerados
valid_extensions = ['.txt', '.bmp', '.bin', '.pgm', '.wav']

# Percorrer todos os arquivos no diretório 'tests'
for filename in os.listdir(test_dir):
    file_path = os.path.join(test_dir, filename)
    # Ignorar diretórios
    if os.path.isdir(file_path):
        continue
    # Ignorar arquivos que já foram comprimidos ou descomprimidos
    if filename.endswith('.lzw') or '_decompressed' in filename:
        continue
    # Ignorar arquivos de estatísticas ou outros arquivos não relevantes
    if filename.endswith('_compress_stats.json') or filename.endswith('_decompress_stats.json'):
        continue
    # Verificar se a extensão é válida
    _, ext = os.path.splitext(filename)
    if ext.lower() in valid_extensions:
        files_to_process.append(filename)
    else:
        print(f"Arquivo com extensão não suportada encontrado e será ignorado: {filename}")

# Função para determinar o tipo de arquivo com base na extensão
def get_file_type(extension):
    if extension == '.txt':
        return 'Texto'
    elif extension in ['.bmp', '.pgm']:
        return 'Imagem'
    elif extension == '.wav':
        return 'Áudio'
    elif extension == '.bin':
        return 'Binário'
    else:
        return 'Desconhecido'

# Listas para os dados de Compressão e Descompressão
compression_data = []
decompression_data = []

# Dicionário para armazenar dados de estatísticas detalhadas para cada arquivo
detailed_stats = {}

# Automatizar a Compressão
for filename in files_to_process:
    input_file = os.path.join(test_dir, filename)
    output_file = os.path.join(test_dir, f'{filename}.lzw')
    stats_file = os.path.join(test_dir, f'{filename}_compress_stats.json')

    # Verifica se o arquivo já foi comprimido
    if os.path.exists(output_file):
        print(f"Arquivo comprimido já existe: {output_file}. Pulando a compressão deste arquivo.")
        continue

    command = [
        'python', 'lzw.py', 'compress', input_file, output_file,
        '--max-bits', '12', '--stats-file', stats_file
    ]

    print(f'Compressing {input_file}...')
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Erro ao comprimir {input_file}:")
        print(result.stderr)
    else:
        print(result.stdout)

# Automatizar a Descompressão
for filename in files_to_process:
    input_file = os.path.join(test_dir, f'{filename}.lzw')
    original_extension = os.path.splitext(filename)[1]
    decompressed_filename = f'{os.path.splitext(filename)[0]}_decompressed{original_extension}'
    output_file = os.path.join(test_dir, decompressed_filename)
    stats_file = os.path.join(test_dir, f'{filename}_decompress_stats.json')

    # Verifica se o arquivo comprimido existe
    if not os.path.exists(input_file):
        print(f"Arquivo comprimido não encontrado: {input_file}. Pulando este arquivo.")
        continue

    # Verifica se o arquivo já foi descomprimido
    if os.path.exists(output_file):
        print(f"Arquivo descomprimido já existe: {output_file}. Pulando a descompressão deste arquivo.")
        continue

    command = [
        'python', 'lzw.py', 'decompress', input_file, output_file,
        '--max-bits', '12', '--stats-file', stats_file
    ]

    print(f'Decompressing {input_file}...')
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Erro ao descomprimir {input_file}:")
        print(result.stderr)
    else:
        print(result.stdout)

# Verificar os Arquivos Descomprimidos
for filename in files_to_process:
    original_file = os.path.join(test_dir, filename)
    original_extension = os.path.splitext(filename)[1]
    decompressed_filename = f'{os.path.splitext(filename)[0]}_decompressed{original_extension}'
    decompressed_file = os.path.join(test_dir, decompressed_filename)

    # Verifica se o arquivo descomprimido existe
    if not os.path.exists(decompressed_file):
        print(f"Arquivo descomprimido não encontrado: {decompressed_file}. Pulando verificação deste arquivo.")
        continue

    # Verifica se o arquivo já foi descomprimido corretamente
    if original_extension.lower() in ['.bmp', '.bin', '.pgm', '.wav']:
        files_are_equal = filecmp.cmp(original_file, decompressed_file, shallow=False)
    else:
        # Para arquivos de texto, podemos comparar como strings
        with open(original_file, 'r', encoding='utf-8') as f1, open(decompressed_file, 'r', encoding='utf-8') as f2:
            files_are_equal = f1.read() == f2.read()
    if files_are_equal:
        print(f'{filename} descomprimido com sucesso.')
    else:
        print(f'Erro: {filename} foi descomprimido incorretamente.')

# Coletar Estatísticas de Compressão e Descompressão
for filename in files_to_process:
    # Caminhos para os arquivos de estatísticas
    compress_stats_file = os.path.join(test_dir, f'{filename}_compress_stats.json')
    decompress_stats_file = os.path.join(test_dir, f'{filename}_decompress_stats.json')

    # Determinar o tipo de arquivo com base na extensão
    _, ext = os.path.splitext(filename)
    ftype = get_file_type(ext.lower())

    # Verifica se o arquivo de estatísticas de compressão existe
    if os.path.exists(compress_stats_file):
        with open(compress_stats_file, 'r') as f:
            compress_stats = json.load(f)

        # Calcular a taxa de compressão com base nos tamanhos dos arquivos
        original_file = os.path.join(test_dir, filename)
        compressed_file = os.path.join(test_dir, f'{filename}.lzw')
        if os.path.exists(original_file) and os.path.exists(compressed_file):
            original_size = os.path.getsize(original_file)
            compressed_size = os.path.getsize(compressed_file)
            compression_ratio = compressed_size / original_size if original_size != 0 else None
        else:
            compression_ratio = None

        # Adicionar dados à lista de compressão
        compression_data.append({
            'File_Name': filename,
            'File_Type': ftype,
            'Compression_Ratio': compression_ratio,
            'Dictionary_Size': compress_stats.get('dictionary_size_over_time', [])[-1] if compress_stats.get('dictionary_size_over_time') else None,
            'Compression_Time(s)': compress_stats.get('execution_time', 0),
            'Memory_Usage(KB)': compress_stats.get('memory_usage', 0)
        })

        # Armazenar estatísticas detalhadas para o arquivo
        detailed_stats[filename] = {
            'compression_ratio_over_time': compress_stats.get('compression_ratio_over_time', []),
            'dictionary_size_over_time': compress_stats.get('dictionary_size_over_time', []),
            'memory_usage': compress_stats.get('memory_usage', 0)
        }

    else:
        print(f"Arquivo de estatísticas de compressão não encontrado: {compress_stats_file}")

    # Verifica se o arquivo de estatísticas de descompressão existe
    if os.path.exists(decompress_stats_file):
        with open(decompress_stats_file, 'r') as f:
            decompress_stats = json.load(f)

        # Adicionar dados à lista de descompressão
        decompression_data.append({
            'File_Name': filename,
            'File_Type': ftype,
            'Decompression_Time(s)': decompress_stats.get('execution_time', 0)
        })
    else:
        print(f"Arquivo de estatísticas de descompressão não encontrado: {decompress_stats_file}")

# Criar DataFrames
compression_df = pd.DataFrame(compression_data)
decompression_df = pd.DataFrame(decompression_data)

# Exibir DataFrames
print("Dados de Compressão:")
display(compression_df)

print("Dados de Descompressão:")
display(decompression_df)

# Função para determinar limites globais para escalas consistentes
def get_global_limits(df, column):
    min_val = df[column].min()
    max_val = df[column].max()
    return min_val, max_val

# Obter limites globais para cada métrica
compression_time_min, compression_time_max = get_global_limits(compression_df, 'Compression_Time(s)') if not compression_df.empty else (0, 1)
decompression_time_min, decompression_time_max = get_global_limits(decompression_df, 'Decompression_Time(s)') if not decompression_df.empty else (0, 1)
compression_ratio_min, compression_ratio_max = get_global_limits(compression_df, 'Compression_Ratio') if not compression_df.empty else (0, 1)
memory_usage_min, memory_usage_max = get_global_limits(compression_df, 'Memory_Usage(KB)') if not compression_df.empty else (0, 1)

# Função para ordenar o DataFrame e retornar a ordem dos arquivos
def get_sorted_order(df, y_column):
    sorted_df = df.sort_values(by=y_column)
    return sorted_df['File_Name']

# 1. Gráfico de Tempo de Compressão e Descompressão Ordenados
fig, axes = plt.subplots(1, 2, figsize=(24, 10))

# Tempo de Compressão
if not compression_df.empty:
    order = get_sorted_order(compression_df, 'Compression_Time(s)')
    sns.barplot(ax=axes[0], x='File_Name', y='Compression_Time(s)', hue='File_Type', data=compression_df, order=order)
    axes[0].set_title('Tempo de Compressão por Arquivo')
    axes[0].set_xlabel('Arquivo')
    axes[0].set_ylabel('Tempo de Compressão (segundos)')
    axes[0].set_ylim(compression_time_min, compression_time_max * 1.1)  # Adiciona 10% para visualização
    axes[0].tick_params(axis='x', rotation=45)
else:
    axes[0].text(0.5, 0.5, 'Nenhum dado de compressão disponível para plotar.', horizontalalignment='center', verticalalignment='center')
    axes[0].set_axis_off()

# Tempo de Descompressão
if not decompression_df.empty:
    order = get_sorted_order(decompression_df, 'Decompression_Time(s)')
    sns.barplot(ax=axes[1], x='File_Name', y='Decompression_Time(s)', hue='File_Type', data=decompression_df, order=order)
    axes[1].set_title('Tempo de Descompressão por Arquivo')
    axes[1].set_xlabel('Arquivo')
    axes[1].set_ylabel('Tempo de Descompressão (segundos)')
    axes[1].set_ylim(decompression_time_min, decompression_time_max * 1.1)
    axes[1].tick_params(axis='x', rotation=45)
else:
    axes[1].text(0.5, 0.5, 'Nenhum dado de descompressão disponível para plotar.', horizontalalignment='center', verticalalignment='center')
    axes[1].set_axis_off()

plt.tight_layout()
plt.show()

# 2. Gráfico de Taxa de Compressão e Uso de Memória Ordenados
fig, axes = plt.subplots(1, 2, figsize=(24, 10))

# Taxa de Compressão
if not compression_df.empty:
    order = get_sorted_order(compression_df, 'Compression_Ratio')
    sns.barplot(ax=axes[0], x='File_Name', y='Compression_Ratio', hue='File_Type', data=compression_df, order=order)
    axes[0].set_title('Taxa de Compressão por Arquivo')
    axes[0].set_xlabel('Arquivo')
    axes[0].set_ylabel('Taxa de Compressão (Comprimido / Original)')
    axes[0].set_ylim(compression_ratio_min * 0.9, compression_ratio_max * 1.1)
    axes[0].tick_params(axis='x', rotation=45)
else:
    axes[0].text(0.5, 0.5, 'Nenhum dado de compressão disponível para plotar.', horizontalalignment='center', verticalalignment='center')
    axes[0].set_axis_off()

# Uso de Memória
if not compression_df.empty:
    order = get_sorted_order(compression_df, 'Memory_Usage(KB)')
    sns.barplot(ax=axes[1], x='File_Name', y='Memory_Usage(KB)', hue='File_Type', data=compression_df, order=order)
    axes[1].set_title('Uso de Memória do Dicionário por Arquivo')
    axes[1].set_xlabel('Arquivo')
    axes[1].set_ylabel('Uso de Memória (KB)')
    axes[1].set_ylim(memory_usage_min * 0.9, memory_usage_max * 1.1)
    axes[1].tick_params(axis='x', rotation=45)
else:
    axes[1].text(0.5, 0.5, 'Nenhum dado de uso de memória disponível para plotar.', horizontalalignment='center', verticalalignment='center')
    axes[1].set_axis_off()

plt.tight_layout()
plt.show()

# 3. Gráficos Detalhados por Arquivo

# Preparar limites globais para os gráficos de Taxa de Compressão e Tamanho do Dicionário
global_compression_ratio_max = max([max(stats['compression_ratio_over_time']) if stats['compression_ratio_over_time'] else 0 for stats in detailed_stats.values()], default=1)
global_dictionary_size_max = max([max(stats['dictionary_size_over_time']) if stats['dictionary_size_over_time'] else 0 for stats in detailed_stats.values()], default=1)

# Plotar Taxa de Compressão ao Longo do Tempo para cada arquivo
for filename in files_to_process:
    if filename in detailed_stats:
        compression_ratio_over_time = detailed_stats[filename]['compression_ratio_over_time']
        if compression_ratio_over_time:
            plt.figure(figsize=(12, 6))
            plt.plot(compression_ratio_over_time)
            plt.title(f'Taxa de Compressão ao Longo do Tempo - {filename}')
            plt.xlabel('Iteração')
            plt.ylabel('Taxa de Compressão')
            plt.ylim(0, global_compression_ratio_max * 1.1)
            plt.grid(True)
            plt.tight_layout()
            plt.show()
        else:
            print(f"Sem dados de taxa de compressão ao longo do tempo para {filename}")
    else:
        print(f"Estatísticas detalhadas não encontradas para {filename}")

# Plotar Tamanho do Dicionário ao Longo do Tempo para cada arquivo
for filename in files_to_process:
    if filename in detailed_stats:
        dictionary_size_over_time = detailed_stats[filename]['dictionary_size_over_time']
        if dictionary_size_over_time:
            plt.figure(figsize=(12, 6))
            plt.plot(dictionary_size_over_time, color='orange')
            plt.title(f'Tamanho do Dicionário ao Longo do Tempo - {filename}')
            plt.xlabel('Iteração')
            plt.ylabel('Tamanho do Dicionário')
            plt.ylim(0, global_dictionary_size_max * 1.1)
            plt.grid(True)
            plt.tight_layout()
            plt.show()
        else:
            print(f"Sem dados de tamanho do dicionário ao longo do tempo para {filename}")
    else:
        print(f"Estatísticas detalhadas não encontradas para {filename}")

# 4. Gráfico Comparativo do Uso de Memória

# Plotar Uso de Memória do Dicionário por Arquivo Ordenados
if not compression_df.empty:
    # Ordenar os arquivos do menor para o maior uso de memória
    compression_df_sorted_memory = compression_df.sort_values(by='Memory_Usage(KB)')
    order = compression_df_sorted_memory['File_Name']
    
    plt.figure(figsize=(18, 10))
    sns.barplot(x='File_Name', y='Memory_Usage(KB)', hue='File_Type', data=compression_df, order=order)
    plt.title('Uso de Memória do Dicionário por Arquivo')
    plt.xlabel('Arquivo')
    plt.ylabel('Uso de Memória (KB)')
    plt.ylim(memory_usage_min * 0.9, memory_usage_max * 1.1)
    plt.xticks(rotation=45)
    plt.legend(title='Tipo de Arquivo')
    plt.tight_layout()
    plt.show()
else:
    print("Nenhum dado de uso de memória disponível para plotar.")
