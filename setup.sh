echo -e "SETUP REQUIRED"
read -p "Masukkan Token Telegram :" token_tele
read -p "Masukkan Admin ID : " admin_id

sudo apt update -y
sudo apt upgrade -y
sudo apt install python3
sudo apt install python3-pip

pip3 install pyTelegramBotAPI
sudo apt-get install sshpass

#Set LocalTime
sudo timedatectl set-timezone Asia/Jakarta


mkdir -p san/bot/buyvpn/akun/sg
mkdir -p san/bot/buyvpn/akun/id
# Pindah ke dalam folder yang baru dibuat
cd san/bot/buyvpn/
# Mengunduh skrip Python
wget https://raw.githubusercontent.com/Sandhj/sanstore/main/sanstore.py
wget https://raw.githubusercontent.com/Sandhj/sanstore/main/reseller.txt

# FOR DO CREATE
TOKEN_TELE="$token_tele"
sed -i "s/{TOKEN_TELE}/$TOKEN_TELE/g" sanstore.py
ADMIN_ID="$admin_id"
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
