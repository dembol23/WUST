def playfair(text, key, mode='encrypt'):
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ" # 25 liter (bez J)
    message = ''
    
    text = text.upper().replace('J', 'I')
    key = key.upper().replace('J', 'I')

    # 1. Budowa macierzy 5x5 na podstawie klucza i alfabetu
    matrix_string = ""
    for char in key + alphabet:
        if char in alphabet and char not in matrix_string:
            matrix_string += char
            
    matrix = [matrix_string[i:i+5] for i in range(0, 25, 5)]

    def find_position(char):
        for row in range(5):
            if char in matrix[row]:
                return row, matrix[row].index(char)
        return -1, -1

    # 2. Przygotowanie tekstu jawnego (tylko poprawne znaki, rozdzielenie par takich samych liter)
    prepared_text = ""
    for char in text:
        if char in alphabet:
            prepared_text += char
            
    digrams = []
    i = 0
    while i < len(prepared_text):
        char1 = prepared_text[i]
        if i + 1 < len(prepared_text):
            char2 = prepared_text[i+1]
            if char1 == char2:
                digrams.append(char1 + 'X')
                i += 1
            else:
                digrams.append(char1 + char2)
                i += 2
        else:
            digrams.append(char1 + 'X')
            i += 1

    # 3. Właściwe szyfrowanie/deszyfrowanie na macierzy
    shift = 1 if mode == 'encrypt' else -1
    
    for char1, char2 in digrams:
        row1, col1 = find_position(char1)
        row2, col2 = find_position(char2)
        
        if row1 == row2: # Ten sam wiersz
            message += matrix[row1][(col1 + shift) % 5]
            message += matrix[row2][(col2 + shift) % 5]
        elif col1 == col2: # Ta sama kolumna
            message += matrix[(row1 + shift) % 5][col1]
            message += matrix[(row2 + shift) % 5][col2]
        else: # Prostokąt
            message += matrix[row1][col2]
            message += matrix[row2][col1]
            
    return message