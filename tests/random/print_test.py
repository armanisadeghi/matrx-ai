from matrx_utils import clear_terminal, vcprint



my_object = {
    "name": "my_object",
    "value": 1
}

some_string_value = "This is a string value"

if __name__ == "__main__":
    clear_terminal()
    vcprint(my_object)
    print()

    vcprint(my_object, color="green")
    print()

    vcprint(my_object, "[TEST TITLE] This is my object", color="blue")
    print()

    vcprint("Just printing some yellow text", color="yellow")
    print()
    
    vcprint(some_string_value, "[TEST TITLE] Some string value", inline=True, color="green")
    print()
