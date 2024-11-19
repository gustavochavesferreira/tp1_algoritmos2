import os
from src.data_structure.trie import *
from typing import Tuple, List
import struct

# Função para converter um conjunto de bytes em um '.txt'
def write_txt_file(decoded_bytes, output_file):
    decoded_string = ''.join([chr(byte) for byte in decoded_bytes])
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(decoded_string)

# Função para converter um conjunto de bytes em um '.bmp' ou '.tiff'
def write_image_file(decoded_bytes, output_file):
    with open(output_file, 'wb') as file:
        file.write(bytes(decoded_bytes))

# Função para remover zeros à esquerda em uma string binárias
def remove_leading_zeros(binary_str):
  return binary_str.lstrip('0') or '0'

# Classe que implementa o algoritmo LZW, empregando árvores Tries Binárias como dicionários
class TrieLZW:
  # Realiza a compressão LZW do arquivo passado como parâmetro
  def compress(self, file_path, compression_type, codes_max_size) -> Tuple[str, str, List]:
    # Utilizando a Trie Compacta Binária como dicionário no algoritmo
    dictionary = CompactTrie()

    # Inicializando todas as chaves de 00000000 até 11111111 no dicionário, com respectivos valores sendo a própria chave
    for num in range(256):
      byte_num = format(num, '08b')
      dictionary.insert(byte_num, byte_num)

    dict_size = 256 # O dicionário começa com todos os símbolos ASCII
    reset = False 

    if(compression_type == "s"):
      num_bits_values = 12 # No caso estático, os códigos terão tamanho 12 bits
      dict_size_limit = 2 ** num_bits_values # Os 12 bits serão suficientes para representar códigos de 000000000000 (0) até 111111111111 (4095) 
    else:
      num_bits_values = 9 # No caso estático dinâmico, os códigos terão tamanho 9 bits inicialmente
      next_dict_size_limit = 512 # Os 9 bits serão suficientes para representar códigos de 000000000 (0) até 111111111 (511)

    # Inicializando variáveis utilizadas pela compressão LZW
    string = ""
    compressed_data = []
    resets = []

    # Aplicando a compressão LZW, considerando cada byte do arquivo original como um símbolo de entrada
    try:
      with open(file_path, "rb") as file:
        while (byte := file.read(1)):
          symbol = bin(int.from_bytes(byte, "big"))[2:].zfill(8)

          string_plus_symbol = string + symbol

          if dictionary.search(string_plus_symbol) != None:
              string = string_plus_symbol
          else:
            # Reiniciando o dicionário no algoritmo estático
            if(compression_type == "s"):
              if(dict_size == dict_size_limit - 1):
                reset = True
            # Expandindo os códigos no algoritmo dinâmico (até o limite)
            else:
              if(dict_size == (2 ** codes_max_size) - 1):
                reset = True
              else:
                if(dict_size == next_dict_size_limit):
                    num_bits_values += 1
                    next_dict_size_limit *= 2

            current_string_formatted_binary_value = dictionary.search(string).value.zfill(num_bits_values)
            compressed_data.append(current_string_formatted_binary_value)
            new_key_value = bin(dict_size)[2:].zfill(num_bits_values)
            dictionary.insert(string_plus_symbol, new_key_value)
            dict_size += 1
            string = symbol

            if(reset):
              reset = False
              dict_size = 256

              if(compression_type != "s"):
                num_bits_values = 9
                next_dict_size_limit = 512

              dictionary = CompactTrie()
              for num in range(256):
                byte_num = format(num, '08b')
                dictionary.insert(byte_num, byte_num)

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
    file_name, file_extension = os.path.splitext(file_path)

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

      return file_name, file_extension

  # Realiza a descompressão LZW do arquivo passado como parâmetro
  def decompress(self, file_path, compression_type, original_file_name, original_file_extension, codes_max_size) -> None:
    # Utilizando a Trie Compacta Binária como dicionário no algoritmo
    dictionary = CompactTrie()

    # Inicializando todas as chaves de 0, 1, 10, 11, 100, ... até 11111111 no dicionário (sem padding), com respectivos valores sendo a própria chave (com padding)
    for num in range(256):
      numeric_key = bin(num)[2:]
      numeric_key_8bit_value = format(num, '08b')
      dictionary.insert(numeric_key, numeric_key_8bit_value)

    dict_size = 256 # O dicionário começa com todos os símbolos ASCII
    reset = False
    if(compression_type == "s"):
      decompression_size = 12 # Sempre puxaremos 12 bits do arquivo comprimido por vez no caso estático
      dict_size_limit = 2 ** decompression_size # Os 12 bits serão suficientes para representar códigos de 000000000000 (0) até 111111111111 (4095)
    else:
      decompression_size = 9 # Começaremos puxando 9 bits do arquivo comprimido por vez
      next_size_limit = 512 # Os 9 bits serão suficientes para representar códigos de 000000000 (0) até 111111111 (511)

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
        if(compression_type == "s"):
          # Caso em que os códigos têm tamanho estático
          if(dict_size == dict_size_limit - 1):
            reset = True
        else:
          # Caso em que os códigos têm tamanho dinâmico
          if(dict_size == 2 ** codes_max_size - 1):
            reset = True
          else:
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

        if(reset):
          reset = False
          dict_size = 256

          if(compression_type != "s"):
            decompression_size = 9
            next_size_limit = 512

          dictionary = CompactTrie()
          for num in range(256):
            numeric_key = bin(num)[2:]
            numeric_key_8bit_value = format(num, '08b')
            dictionary.insert(numeric_key, numeric_key_8bit_value)

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

    # Gerando o arquivo inicial
    switch = {
        '.txt': write_txt_file,
        '.bmp': write_image_file,
        '.tiff': write_image_file
        }
    
    handler = switch.get(original_file_extension)

    if handler:
        handler(bytes_, f"decompressed_{original_file_name}{original_file_extension}")
    else:
        print("Tipo de arquivo não suportado!")