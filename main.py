import os
import argparse

from src.compressor.lzw import TrieLZW

def are_files_identical(file1, file2):
    try:
        with open(file1, "rb") as f1, open(file2, "rb") as f2:
            while True:
                chunk1 = f1.read(4096) 
                chunk2 = f2.read(4096)
                if chunk1 != chunk2: 
                    return False
                if not chunk1:
                    return True
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return False
    
def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--file_name", type=str, required=True, help="Arquivo a ser comprimido")
    parser.add_argument("--compression_mode", type=str, required=True, help="Modo de compressão (s para estático e d para dinâmico)")
    parser.add_argument("--stats", type=str, required=True, help="Gerar estatísticas do processo? (s) para sim e (n) para não")
    parser.add_argument("--max_codes_size", type=int, required=False, help="Tamanho máximo dos códigos")

    args = parser.parse_args()

    lzw = TrieLZW()

    (file_name, file_extension) = lzw.compress(args.file_name, args.compression_mode, {args.max_codes_size if args.max_codes_size else 12})

    compressed_file = f"compressed_{args.file_name}.bin"

    lzw.decompress(args.file_name, args.compression_mode, file_name, file_extension, {args.max_codes_size if args.max_codes_size else 12})
    
    original_file_size = os.path.getsize(args.file_name)
    compressed_file_size = os.path.getsize(compressed_file)

    print(f"Tamanho do arquivo original: {original_file_size} bytes.")
    print(f"Tamanho do arquivo comprimido: {compressed_file_size} bytes.")
    
    txt_file1 = args.file_name
    txt_file2 = f"decompressed_{args.file_name}"
    print(txt_file1)
    print(txt_file2)
    print("Os arquivos .txt são iguais? " + ("Sim" if are_files_identical(txt_file1, txt_file2) else "Não"))

if __name__ == "__main__":
    main()
