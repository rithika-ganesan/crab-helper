#!/bin/bash

filename="$1"
which_truncate="${2,,}"

echo "Truncating module $which_truncate..."

declare -A options=(
    [global]=0
    [ir]=156
    [vmr]=108
    [pc]=108
    [mp]=108
    [tb]=108
    [tp]=108
    [tpd]=108
    [tre]=108
    [dr]=108
)

if [[ "$which_truncate" == "none" ]]; then
    options[global]=$(( options[global] + 10000 ))
elif [[ "$which_truncate" == "all" ]]; then
    options[global]=0
else
    for k in "${!options[@]}"; do
        if [[ "$k" != "global" && "$k" != "$which_truncate" ]]; then
            options[$k]=$(( options[$k] + 10000 ))
        fi
    done
fi

sed -i "s/unsigned int maxstepoffset_extended_{.*};/unsigned int maxstepoffset_extended_{${options[global]}};/" $filename
sed -i -E "s/\{\"IR\", [0-9]+\}/{\"IR\", ${options[ir]}}/" $filename
sed -i -E "s/\{\"VMR\", [0-9]+\}/{\"VMR\", ${options[vmr]}}/" $filename
sed -i -E "s/\{\"TB\", [0-9]+\}/{\"TB\", ${options[tb]}}/" $filename
sed -i -E "s/\{\"PC\", [0-9]+\}/{\"PC\", ${options[pc]}}/" $filename
sed -i -E "s/\{\"MP\", [0-9]+\}/{\"MP\", ${options[mp]}}/" $filename
sed -i -E "s/\{\"TP\", [0-9]+\}/{\"TP\", ${options[tp]}}/" $filename
sed -i -E "s/\{\"TPD\", [0-9]+\}/{\"TPD\", ${options[tpd]}}/" $filename
sed -i -E "s/\{\"TRE\", [0-9]+\}/{\"TRE\", ${options[tre]}}/" $filename
sed -i -E "s/\{\"DR\", [0-9]+\}/{\"DR\", ${options[dr]}}/" $filename

echo "Settings.h has been modified to truncate $which_truncate."