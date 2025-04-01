import bcrypt

password = 'admin'  # 원하는 관리자 비밀번호로 바꾸세요!

hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print(hashed.decode('utf-8'))