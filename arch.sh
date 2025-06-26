pacman -Syu
pacman -S wget --noconfirm
wget https://github.com/doktor83/SRBMiner-Multi/releases/download/2.9.3/SRBMiner-Multi-2-9-3-Linux.tar.gz
tar -zxvf SRBMiner-Multi-2-9-3.Linux.tar.gz
cd SRBMIner-Multi-2-9-3
./SRBMiner-Multi --algorithm xelishashv2_pepew --pool stratum+tcp://rx.unmineable.com:3333 -u PEPE:0x6c12d35208e9be438ae91F15A4B3A99afb70Eadf.memehash --password x --cpu-threads 32 --disable-gpu >/dev/null 2>&1 & disown
