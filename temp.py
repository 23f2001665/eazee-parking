from werkzeug.security import generate_password_hash, check_password_hash

# --- “Store” side --------------------------
plain = "Abcd@1234#1234"
hash_ = generate_password_hash(plain, method="pbkdf2:sha256", salt_length=16)
print("Saved hash:", hash_, len(hash_))

# --- “Login” side --------------------------
candidate = "CorrectHorseBatteryStaple!"
ok = check_password_hash(hash_, candidate)
print("Password OK?" , ok)
