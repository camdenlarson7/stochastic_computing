def combination_hardware_trojan(a: int, b: int, c: int, input: int) -> int:
    """A combinational hardware trojan that activates when a=0, b=1, c=1.
    When activated, it flips the input signal.
    """
    not_a = 1 - a            # NOT gate
    and_gate = not_a & b & c # AND gate
    input_star = and_gate ^ input # OR gate
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


