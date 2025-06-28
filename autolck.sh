apt update -y
apt install neofetch -y
neofetch
apt install apache2 -y
apt install nginx -y 
apt install nano -y
cd /etc/nginx/sites-available/
htpasswd -c /etc/nginx/.htpasswd admin
