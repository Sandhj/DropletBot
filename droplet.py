import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import requests
import time

# Masukkan token bot telegram Anda di sini
TOKEN = '{TOKEN_TELE}'

# Masukkan token API DigitalOcean Anda di sini
DO_TOKEN = '{TOKEN_DO}'

# URL endpoint untuk membuat droplet di DigitalOcean
DO_DROPLET_URL = 'https://api.digitalocean.com/v2/droplets'

# Default root password
ROOT_PASSWORD = '{PASS_VPS}'

# Inisialisasi objek bot
bot = telebot.TeleBot(TOKEN)

# Dictionary untuk memetakan opsi ukuran dengan kode ukuran DigitalOcean yang sesuai
size_options = {
    '1 TB / 1GB RAM': 's-1vcpu-1gb-amd',
    '2 TB / 2GB RAM': 's-1vcpu-2gb-amd',
    '3 TB / 2GB RAM': 's-2vcpu-2gb-amd',
    '4 TB / 4GB RAM': 's-2vcpu-4gb-amd',
    '5 TB / 8GB RAM': 's-4vcpu-8gb-amd',
    # Tambahkan lebih banyak opsi ukuran jika diperlukan
}

# Dictionary untuk menyimpan data sementara pengguna
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    start_keyboard = InlineKeyboardMarkup(row_width=2)
    create_button = InlineKeyboardButton(text='CREATE', callback_data='create_droplet')
    delete_button = InlineKeyboardButton(text='DELETE', callback_data='delete_droplet')
    start_keyboard.add(create_button, delete_button)
    bot.send_message(chat_id, '🤖Bot Simple For Create and Delete Droplet Digital Ocean. Author San', reply_markup=start_keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'create_droplet')
def handle_create_callback(call: CallbackQuery):
    request_droplet_name(call.message)

@bot.callback_query_handler(func=lambda call: call.data == 'delete_droplet')
def handle_delete_callback(call: CallbackQuery):
    bot.send_message(call.message.chat.id, 'Masukkan ID droplet yang akan dihapus:')
    bot.register_next_step_handler(call.message, handle_delete_droplet_step)

@bot.message_handler(commands=['create'])
def request_droplet_name(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Masukkan nama droplet:')
    bot.register_next_step_handler(message, request_droplet_image)

def request_droplet_image(message):
    chat_id = message.chat.id
    droplet_name = message.text
    user_data[chat_id] = {'name': droplet_name}  # Simpan nama droplet di user_data
    # Membuat InlineKeyboard untuk memilih image
    image_keyboard = InlineKeyboardMarkup(row_width=2)
    ubuntu_button = InlineKeyboardButton(text='Ubuntu 20.04', callback_data='image_ubuntu-20-04-x64')
    debian_button = InlineKeyboardButton(text='Debian 10', callback_data='image_debian-10-x64')
    image_keyboard.add(ubuntu_button, debian_button)
    
    bot.send_message(chat_id, 'Pilih image untuk droplet:', reply_markup=image_keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('image_'))
def handle_image_callback(call: CallbackQuery):
    chat_id = call.message.chat.id
    image_code = call.data.split('_')[1]  # Mendapatkan kode image dari data callback
    user_data[chat_id]['image'] = image_code  # Simpan image di user_data

    # Membuat InlineKeyboard untuk memilih ukuran droplet
    size_keyboard = InlineKeyboardMarkup(row_width=1)
    for size_label, size_code in size_options.items():
        button = InlineKeyboardButton(text=size_label, callback_data=f"size_{size_code}")
        size_keyboard.add(button)
    
    bot.send_message(chat_id, 'Pilih ukuran droplet:', reply_markup=size_keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('size_'))
def handle_size_callback(call: CallbackQuery):
    chat_id = call.message.chat.id
    size_code = call.data.split('_')[1]  # Mendapatkan kode ukuran dari data callback
    droplet_name = user_data.get(chat_id, {}).get('name')  # Mendapatkan nama droplet dari user_data
    image_code = user_data.get(chat_id, {}).get('image')  # Mendapatkan image dari user_data

    if not droplet_name or not image_code:
        bot.send_message(chat_id, 'Terjadi kesalahan. Silakan mulai lagi.')
        return

    if size_code not in size_options.values():
        bot.send_message(chat_id, 'Ukuran droplet tidak valid. Silakan coba lagi.')
        return

    # Parameter lain untuk membuat droplet
    region = 'sgp1'  
    
    # Membuat payload untuk request API DigitalOcean
    data = {
        'name': droplet_name,
        'region': region,
        'size': size_code,
        'image': image_code,
        'user_data': f'''#!/bin/bash
                        useradd -m -s /bin/bash root
                        echo "root:{ROOT_PASSWORD}" | chpasswd
                        '''
    }
    
    # Header untuk autentikasi dengan token API DigitalOcean
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {DO_TOKEN}'
    }
    
    # Mengirim request untuk membuat droplet
    response = requests.post(DO_DROPLET_URL, json=data, headers=headers)
    
    if response.status_code == 202:
        bot.send_message(chat_id, 'Droplet berhasil dibuat! Menunggu 60 detik sebelum mengambil informasi...')
        time.sleep(60)
        droplet_info = get_droplet_info(response.json()['droplet']['id'])
        if droplet_info:
            respon = "INFORMASI DROPLET\n"
            respon += f"NAMA: {droplet_info['name']}\n"
            respon += f"ID: {droplet_info['id']}\n"
            respon += f"IP: {droplet_info['ip_address']}"
            bot.send_message(chat_id, respon)
        else:
            bot.send_message(chat_id, 'Gagal mengambil informasi droplet.')
    else:
        bot.send_message(chat_id, 'Gagal membuat droplet. Silakan coba lagi.')

def get_droplet_info(droplet_id):
    droplet_info_url = f"{DO_DROPLET_URL}/{droplet_id}"
    headers = {
        'Authorization': f'Bearer {DO_TOKEN}'
    }
    response = requests.get(droplet_info_url, headers=headers)
    if response.status_code == 200:
        droplet_info = response.json()['droplet']
        return {
            'id': droplet_info['id'],
            'name': droplet_info['name'],
            'ip_address': droplet_info['networks']['v4'][0]['ip_address']
        }
    else:
        return None

# Fungsi untuk menghapus droplet berdasarkan ID
def delete_droplet(droplet_id):
    url = f'https://api.digitalocean.com/v2/droplets/{droplet_id}'
    headers = {'Authorization': f'Bearer {DO_TOKEN}'}
    response = requests.delete(url, headers=headers)
    return response.status_code == 204

# Fungsi yang menangani langkah penghapusan droplet
def handle_delete_droplet_step(message):
    droplet_id = message.text.strip()
    if delete_droplet(droplet_id):
        bot.reply_to(message, f"Droplet dengan ID {droplet_id} berhasil dihapus.")
    else:
        bot.reply_to(message, f"Droplet dengan ID {droplet_id} tidak ditemukan atau gagal dihapus.")

# Start bot polling
bot.polling()
