import os
import pickle
from cryptography.fernet import Fernet

def reset_ip_lock(ip_to_reset):
    # Получаем SECRET_KEY из переменных окружения
    key = os.environ.get('SECRET_KEY')
    if key is None:
        print("Не установлен SECRET_KEY.")
        return

    try:
        # Шаг 1: Загрузить зашифрованные данные
        with open('auth_state.pkl', 'rb') as f:
            encrypted_data = f.read()

        # Шаг 2: Расшифровать данные
        key = key.encode()
        fernet = Fernet(key)
        data = pickle.loads(fernet.decrypt(encrypted_data))

        # Шаг 3: Изменить данные
        ip_attempts = data.get('ip_attempts', {})
        if ip_to_reset in ip_attempts:
            ip_attempts[ip_to_reset]['attempts'] = 0
            ip_attempts[ip_to_reset]['locked_until'] = None  # Сбросить блокировку
            print(f"Блокировка для IP {ip_to_reset} сброшена.")
        else:
            print(f"IP {ip_to_reset} не найден в записях.")

        # Шаг 4: Зашифровать измененные данные и записать обратно в файл
        data['ip_attempts'] = ip_attempts
        encrypted_data = fernet.encrypt(pickle.dumps(data))

        with open('auth_state.pkl', 'wb') as f:
            f.write(encrypted_data)

    except FileNotFoundError:
        print("Файл состояния не найден.")
    except Exception as e:
        print(f"Ошибка: {str(e)}")

# Пример использования
reset_ip_lock('5.139.225.211')  # Замените на нужный IP-адрес