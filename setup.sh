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
sed -i "s/{TOKEN_TELE}/$TOKEN_TELE/g" droplet.py
TOKEN_DO="$token_do"
sed -i "s/{TOKEN_DO}/$TOKEN_DO/g" droplet.py
PASS_DO="$pass_do"
sed -i "s/{PASS_VPS}/$PASS_DO/g" droplet.py

# fungsi running as system
cd
cat << 'EOF' > /etc/systemd/system/droplet.service
[Unit]
Description=Telegram Bot
After=network.target

[Service]
User=root
WorkingDirectory=/root/san/bot/droplet
ExecStart=/usr/bin/python3 droplet.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start droplet
sudo systemctl enable droplet
sudo systemctl restart droplet

echo "Instalasi selesai."

cd
rm setup.sh
