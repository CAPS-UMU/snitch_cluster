# bash clean-up-logs.sh 

cd ..

clean(){
     FILE="$1"
     rm -rf $FILE
    
}

# find files to clean up
find . -name dma_trace_00008_00000.log > to-clean.txt
find . -name trace_hart_00000.txt >> to-clean.txt
find . -name trace_hart_00001.txt >> to-clean.txt
find . -name trace_hart_00002.txt >> to-clean.txt
find . -name trace_hart_00003.txt >> to-clean.txt
find . -name trace_hart_00004.txt >> to-clean.txt
find . -name trace_hart_00005.txt >> to-clean.txt
find . -name trace_hart_00006.txt >> to-clean.txt
find . -name trace_hart_00007.txt >> to-clean.txt

# clean up all the files
while read -r line
do
    echo "$line"
    clean "$line"
done < "to-clean.txt"

cd myrtle-experiments

