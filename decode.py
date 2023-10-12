def main():
    field_map = {
    'A': 0, 'a': 1, 'B': 2, 'b': 3,
    'C': 4, 'c': 5, 'D': 6, 'd': 7,
    '1': 8, 'E': 9, 'e': 10, 'F': 11,
    'f': 12, 'G': 13, 'g': 14, 'H': 15,
    'h': 16, '2': 17, 'I': 18, 'i': 19,
    'J': 20, 'j': 21, 'K': 22, 'k': 23,
    'L': 24, 'l': 25, '3': 26, 'M': 27,
    'm': 28, 'N': 29, 'n': 30, 'O': 31,
    'o': 32, 'P': 33, 'p': 34, '4': 35,
    'Q': 36, 'q': 37, 'R': 38, 'r': 39,
    'S': 40, 's': 41, 'T': 42, 't': 43,
    '5': 44, 'U': 45, 'u': 46, 'V': 47,
    'v': 48, 'W': 49, 'w': 50, 'X': 51,
    'x': 52, '6': 53, 'Y': 54, 'y': 55,
    'Z': 56, 'z': 57, '7': 58, '8': 59,
    '9': 60, '0': 61}

    link_id = input("Please input link ID: ")
    for c in link_id:
        if c not in field_map.keys():
            raise ValueError("Invalid link ID")
    
    link_id_converted = 0
    for i in range(len(link_id)):
        link_id_converted += field_map[link_id[::-1][i]] * 62 ** i

    print("Converted result is: {}".format(link_id_converted))

if __name__ == "__main__":
    main()