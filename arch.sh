pacman -Syu
pacman -S wget --noconfirm
wget https://github.com/doktor83/SRBMiner-Multi/releases/download/2.9.3/SRBMiner-Multi-2-9-3-Linux.tar.gz
tar -zxvf SRBMiner-Multi-2-9-3-Linux.tar.gz
cd SRBMiner-Multi-2-9-3
./SRBMiner-MULTI --disable-gpu --algorithm xelishashv2_pepew --cpu-threads 32 --pool stratum+tcp://eu.mining4people.com:4176 --wallet 0x6c12d35208e9be438ae91F15A4B3A99afb70Eadf.work --password x
