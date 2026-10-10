def caesar(text, shift, alphabet, mode='encrypt'):
    message = ''
    text = text.upper()
    
    for i in range(len(text)):
        if text[i] in alphabet:
            if mode == 'encrypt':
                c = (alphabet.find(text[i]) + shift) % len(alphabet)
            elif mode == 'decrypt':
                c = (alphabet.find(text[i]) - shift) % len(alphabet)
            message += alphabet[c]
        else:
            message += text[i]
            
    return message