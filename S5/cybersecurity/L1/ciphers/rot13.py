def rot13(text, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    message = ''
    text = text.upper()
    
    for i in range(len(text)):
        if text[i] in alphabet:
            # W ROT13 szyfrowanie i deszyfrowanie to zawsze przesunięcie o połowę alfabetu (13)
            c = (alphabet.find(text[i]) + 13) % len(alphabet)
            message += alphabet[c]
        else:
            message += text[i]
            
    return message