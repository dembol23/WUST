def vigenere(text, key, alphabet, mode='encrypt'):
  message = ''
  key_len = len(key)
  text = text.upper()
  key = key.upper()
 
  for i in range(len(text)):
    if text[i] in alphabet:
      if mode == 'encrypt':
        c = (alphabet.find(text[i]) + (alphabet.find(key[i % key_len]))) % len(alphabet)
      elif mode == 'decrypt':
        c = (alphabet.find(text[i]) - (alphabet.find(key[i % key_len]))) % len(alphabet)
      message += alphabet[c]
    else:
      message += text[i]
 
  return message