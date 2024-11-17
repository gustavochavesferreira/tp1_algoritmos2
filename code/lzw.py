import argparse
import time
import json
import sys
import os
import tracemalloc

class BitWriter:
    def __init__(self, file):
        self.file = file
        self.buffer = 0
        self.buffer_size = 0  # Número de bits atualmente no buffer

    def write_bits(self, data, num_bits):
        while num_bits > 0:
            remaining = 8 - self.buffer_size
            bits_to_write = min(num_bits, remaining)
            # Extrai os bits mais significativos
            bits = (data >> (num_bits - bits_to_write)) & ((1 << bits_to_write) - 1)
            self.buffer = (self.buffer << bits_to_write) | bits
            self.buffer_size += bits_to_write
            num_bits -= bits_to_write

            if self.buffer_size == 8:
                self.file.write(bytes([self.buffer]))
                self.buffer = 0
                self.buffer_size = 0

    def flush(self):
        if self.buffer_size > 0:
            self.buffer = self.buffer << (8 - self.buffer_size)
            self.file.write(bytes([self.buffer]))
            self.buffer = 0
            self.buffer_size = 0

class BitReader:
    def __init__(self, file):
        self.file = file
        self.buffer = 0
        self.buffer_size = 0  # Número de bits atualmente no buffer

    def read_bits(self, num_bits):
        result = 0
        while num_bits > 0:
            if self.buffer_size == 0:
                byte = self.file.read(1)
                if not byte:
                    return None  # Fim do arquivo
                self.buffer = byte[0]
                self.buffer_size = 8

            bits_to_read = min(num_bits, self.buffer_size)
            result = (result << bits_to_read) | ((self.buffer >> (self.buffer_size - bits_to_read)) & ((1 << bits_to_read) - 1))
            self.buffer_size -= bits_to_read
            num_bits -= bits_to_read
        return result

class LZW:
    def __init__(self, max_bits=12):
        self.max_bits = max_bits
        self.max_table_size = 2 ** self.max_bits
        self.stats = {
            'compression_ratio_over_time': [],
            'dictionary_size_over_time': [],
            'execution_time': 0,
            'memory_usage': 0
        }

    def compress(self, input_data):
        start_time = time.time()
        tracemalloc.start()  

        # Inicializa o dicionário com bytes individuais
        dictionary = {bytes([i]): i for i in range(256)}
        string = b""
        compressed_data = []
        code = 256

        for symbol in input_data:
            symbol_byte = bytes([symbol])
            string_plus_symbol = string + symbol_byte
            if string_plus_symbol in dictionary:
                string = string_plus_symbol
            else:
                compressed_data.append(dictionary[string])
                if len(dictionary) < self.max_table_size:
                    dictionary[string_plus_symbol] = code
                    code += 1
                    self.stats['dictionary_size_over_time'].append(len(dictionary))
                string = symbol_byte

                # Atualiza estatísticas
                compressed_size = len(compressed_data) * self.max_bits
                original_size = len(input_data) * 8  # Assume 8 bits por byte
                compression_ratio = compressed_size / original_size
                self.stats['compression_ratio_over_time'].append(compression_ratio)

        if string:
            compressed_data.append(dictionary[string])

        # Calcula o tempo
        end_time = time.time()
        self.stats['execution_time'] = end_time - start_time

        # Calcula o uso de memória
        _, peak_memory = tracemalloc.get_traced_memory()
        self.stats['memory_usage'] = peak_memory / 1024  # Converte para KB
        tracemalloc.stop()

        return compressed_data

    def decompress(self, compressed_data):
        start_time = time.time()
        tracemalloc.start()


        # Inicializa o dicionário com bytes individuais
        dictionary = {i: bytes([i]) for i in range(256)}
        result = bytearray()
        code = 256

        if not compressed_data:
            print("Erro: Dados comprimidos estão vazios.")
            return bytes(result)

        prev_code = compressed_data.pop(0)
        string = dictionary[prev_code]
        result.extend(string)

        for curr_code in compressed_data:
            if curr_code in dictionary:
                entry = dictionary[curr_code]
            elif curr_code == code:
                entry = string + string[:1]
            else:
                raise ValueError(f"Código inválido: {curr_code}")

            result.extend(entry)

            if len(dictionary) < self.max_table_size:
                dictionary[code] = string + entry[:1]
                code += 1
                self.stats['dictionary_size_over_time'].append(len(dictionary))

            string = entry

        # Calcula o tempo
        end_time = time.time()
        self.stats['execution_time'] = end_time - start_time

        # Calcula o uso de memória
        _, peak_memory = tracemalloc.get_traced_memory()
        self.stats['memory_usage'] = peak_memory / 1024
        tracemalloc.stop()

        return bytes(result)

def run_lzw(mode, input_file, output_file, max_bits=12, stats_file=None):
    lzw = LZW(max_bits=max_bits)

    if mode == "compress":
        # Lê o arquivo de entrada em modo binário
        with open(input_file, "rb") as file:
            input_data = file.read()

        # Realiza a compressão
        compressed_data = lzw.compress(input_data)
        # print(f"Códigos comprimidos: {compressed_data}")
        
        # Escreve os dados comprimidos usando BitWriter
        with open(output_file, "wb") as file:
            bit_writer = BitWriter(file)
            for data in compressed_data:
                bit_writer.write_bits(data, lzw.max_bits)
            bit_writer.flush()

        print(f"Compressão concluída. Arquivo salvo em {output_file}")

        # Calcula a taxa de compressão
        compressed_size = len(compressed_data) * max_bits
        original_size = len(input_data) * 8  # Assume 8 bits por byte
        compression_ratio = compressed_size / original_size

        # Exporta os dados comprimidos para um arquivo JSON
        compressed_json_file = output_file + ".json"
        with open(compressed_json_file, "w") as json_file:
            json.dump(compressed_data, json_file, indent=4)
        print(f"Códigos comprimidos salvos em {compressed_json_file}")

        # Salva as estatísticas se solicitado
        if stats_file:
            stats = {
                'compression_ratio_over_time': lzw.stats['compression_ratio_over_time'],
                'dictionary_size_over_time': lzw.stats['dictionary_size_over_time'],
                'execution_time': lzw.stats['execution_time'],
                'memory_usage': lzw.stats['memory_usage']
            }
            with open(stats_file, "w") as f:
                json.dump(stats, f, indent=4)
            print(f"Estatísticas salvas em {stats_file}")

    elif mode == "decompress":
        print(f"Iniciando descompressão de {input_file}...")
        # Lê os dados comprimidos usando BitReader
        compressed_data = []
        with open(input_file, "rb") as file:
            bit_reader = BitReader(file)
            while True:
                data = bit_reader.read_bits(lzw.max_bits)
                if data is None:
                    break
                compressed_data.append(data)

        print(f"Comprimento dos dados comprimidos: {len(compressed_data)}")

        if not compressed_data:
            print("Erro: Arquivo comprimido está vazio ou corrompido.")
            sys.exit(1)

        # Realiza a descompressão
        try:
            decompressed_data = lzw.decompress(compressed_data)
        except Exception as e:
            print(f"Erro durante a descompressão: {e}")
            sys.exit(1)

        # print(f"Dados descomprimidos: {decompressed_data.decode('utf-8', errors='ignore')}")
        print(f"Comprimento dos dados descomprimidos: {len(decompressed_data)}")

        # Escreve os dados descomprimidos em modo binário
        with open(output_file, "wb") as file:
            file.write(decompressed_data)

        print(f"Descompressão concluída. Arquivo salvo em {output_file}")

        # Salva as estatísticas se solicitado
        if stats_file:
            stats = {
                'execution_time': lzw.stats['execution_time'],
                'memory_usage': lzw.stats['memory_usage']
            }
            with open(stats_file, "w") as f:
                json.dump(stats, f, indent=4)
            print(f"Estatísticas salvas em {stats_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compressão e Descompressão usando LZW")
    parser.add_argument("mode", choices=["compress", "decompress"], help="Modo de operação")
    parser.add_argument("input_file", help="Arquivo de entrada")
    parser.add_argument("output_file", help="Arquivo de saída")
    parser.add_argument("--max-bits", type=int, default=12, help="Número máximo de bits (padrão: 12)")
    parser.add_argument("--stats-file", help="Arquivo para salvar estatísticas em formato JSON")

    # Verifica se está em um ambiente interativo
    if 'ipykernel' in sys.modules:
        # Defina os argumentos manualmente para testes no notebook
        # Ajuste conforme necessário para testes
        args = parser.parse_args([
            'compress',            # ou 'decompress' conforme necessário
            'input.txt',           # Substitua pelo arquivo de entrada correto
            'output.lzw',          # Substitua pelo arquivo de saída correto
            '--max-bits', '12',
            '--stats-file', 'stats.json'
        ])
    else:
        args = parser.parse_args()

    run_lzw(args.mode, args.input_file, args.output_file, args.max_bits, args.stats_file)
