pacman -S mingw-w64-x86_64-curl --noconfirm
pacman -S base-devel curl libcurl-compat libcurl-gnutls
./configure
make
sudo make install
sudo pacman -S jansson openssl
cpuminer --version
