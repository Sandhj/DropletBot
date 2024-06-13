echo -e "SETUP REQUIRED"
read -p "Masukkan Token Telegram :" token_tele
read -p "Masukkan Token DO : " token_do
read -p "Password Default VPS: " pass_do

sudo apt update -y
sudo apt upgrade -y
sudo apt install python3
sudo apt install python3-pip

pip3 install pyTelegramBotAPI

#Set LocalTime
sudo timedatectl set-timezone Asia/Jakarta


mkdir -p san/bot/droplet
# Pindah ke dalam folder yang baru dibuat
cd san/bot/droplet
# Mengunduh skrip Python
wget https://raw.githubusercontent.com/Sandhj/DropletBot/main/droplet.py

# FOR DO CREATE
TOKEN_TELE="$token_tele"
sed -i "s/{TOKEN_TELE}/$TOKEN_TELE/g" sanstore.py
TOKEN_DO="$token_do"
sed -i "s/{ADMIN_ID}/$ADMIN_ID/g" sanstore.py

# fungsi running as system
cd
cd /etc/systemd/system
wget https://raw.githubusercontent.com/Sandhj/sanstore/main/sanstore.service
sudo systemctl daemon-reload
sudo systemctl start sanstore
sudo systemctl enable sanstore
sudo systemctl restart sanstore

echo "Instalasi selesai."

cd
rm setup.sh
