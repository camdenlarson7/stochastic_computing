def combination_hardware_trojan(a: int, b: int, c: int, d: int, e: int, input_bit: int) -> int:
    """Combinational hardware trojan that activates when:
       a == 0, b == 1, c == 1, d == 1, e == 1 (i.e., (not a) & b & c & d & e).
       When activated, it flips the input bit.
    """
    not_a = 1 - a
    and_gate = not_a & b & c & d & e
    input_star = and_gate ^ input_bit
    return input_star


def main():
    for a in [0,1]:
        for b in [0,1]:
            for c in [0,1]:
                for input in [0,1]:
                    if (input != combination_hardware_trojan(a,b,c,input)):
                        print(f"Trojan activated with a={a}, b={b}, c={c}, input={input} => input*={combination_hardware_trojan(a,b,c,input)}")
                
                    print(f"a={a}, b={b}, c={c}, input={input} => input*={combination_hardware_trojan(a,b,c,input)}")
                    

if __name__ == "__main__": 
    main()


