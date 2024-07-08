#!/bin/bash -l
#SBATCH --job-name=test
#SBATCH --time=00:15:00
#SBATCH --partition=debug
# #SBATCH --qos=short
#SBATCH --error=test.err
#SBATCH --output=test.out
#SBATCH --ntasks-per-core=1

while getopts "p:w:e:out_file:para:" opt
do
  case $opt in 
    p) path="$OPTARG"
    ;;
    w) weight_rel="$OPTARG"
    ;;
  esac
done

echo $path > test_path
echo asdfasfd
echo 12345