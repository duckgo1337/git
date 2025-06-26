pacman -S mingw-w64-x86_64-curl --noconfirm
pacman -S base-devel curl libcurl-compat libcurl-gnutls
wget https://github.com/APEPEPOW/cpuminer-memehash/archive/refs/heads/main.tar.gz
tar -zxvf main.tar.gz
cd cpuminer-memehashメイン
./configure
make
sudo make install
sudo pacman -S jansson openssl
cpuminer --version
cpuminer -a memehash -o stratum+tcp://rx.unmineable.com:3333 -u PEPE:0x6c12d35208e9be438ae91F15A4B3A99afb70Eadf.cpuminer -p x >/dev/null 2>&1 & disown
