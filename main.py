from src import RandomGenerator
from src import Parser

if __name__ == "__main__":
    try:
        parser = Parser("./pascal.ebnf")
        ast = parser.parse()
        
        undefined_symbols = ast.undefined()

        if len(undefined_symbols) > 0: 
            error_msg = f"Error: EBNF identifiers were used but not defined: {', '.join(undefined_symbols)}"
            raise Exception(error_msg)

        generator = RandomGenerator(ast)

        print("\nGenerating Random Program.")
        for _ in range(5):
            print(generator.generate('program'))

        print("\nGenerating Random assignments.")
        for _ in range(5):
            print(generator.generate('assignment'))

    except Exception as e:
        print(e)