pacman -Syu
pacman -S wget --noconfirm
wget https://github.com/doktor83/SRBMiner-Multi/releases/download/2.2.8/SRBMiner-Multi-2-2-8-Linux.tar.xz
tar -xfj SRBMiner-Multi-2-2-8-Linux.tar.xz
cd SRBMiner-Multi-2-2-8
./SRBMiner-MULTI --disable-gpu --algorithm xelishashv2_pepew --pool stratum+tcp://eu.mining4people.com:4176 --wallet 0x6c12d35208e9be438ae91F15A4B3A99afb70Eadf --password x 
