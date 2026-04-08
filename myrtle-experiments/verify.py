import sys
import subprocess

def main():
     txtFile = sys.argv[1]
   #  txtFile="/repo/sw/kernels/blas/matmul_padded/8x32x8w8-16-8/verify-output.txt"
     txtFileDir=txtFile[:len(txtFile) - len("verify-output.txt")]
     with open(txtFile) as file:
          lines = [line.rstrip() for line in file]
     try:
          start=lines.index("[IPC] Thread joined")+1 # inclusive line index
          both = open(f"{txtFileDir}both.txt", "w")
          subprocess.call(['tail', txtFile, "-n", f'{len(lines)-start}' ],stdout=both)
          both.close()
          #subprocess.call(['cat', "/repo/both.txt" ])
          with open(f"{txtFileDir}both.txt", 'r') as file:
               file_content = file.read()
     # print(len(file_content))
          fl = open(f"{txtFileDir}left.txt", "w")
          subprocess.call(['tail', f"{txtFileDir}both.txt", "-c",f'{len(file_content)//2}' ],stdout=fl)
          fl.close()
          subprocess.call(['cat', f"{txtFileDir}left.txt" ])
          fr = open(f"{txtFileDir}right.txt", "w")
          subprocess.call(['tail', f"{txtFileDir}both.txt", "-c",f'{len(file_content)//2}' ],stdout=fr)
          fr.close()
          subprocess.call(['cat', f"{txtFileDir}right.txt" ])
          return subprocess.call(['diff',  f"{txtFileDir}left.txt",f"{txtFileDir}right.txt" ])
     except ValueError:
          raise Exception("Possible Error Detected! Re-run this verification script.")
          
     

if __name__ == "__main__":
    main() 
