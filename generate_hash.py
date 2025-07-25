from hashlib import sha256

# Replace 'Your Password' with your desired password. Default is 'Password' You must put it in quotes.
password = 'Your Password'
hashed = sha256(password.encode()).hexdigest()
print(f"Your password hash is: {hashed}")