# LS-8: 8-Bit Computer Emulator V1.0

In this project, we attempted to implement a turing complete emulator of an 8-bit CPU in Python, the pedagogical purpose of the assignment being to understand more deeply how a programming language works. Through the creation of virtual RAM, the use of binary and hexadecimal integers, as well as subroutine CALL and RETURN functions, I definitely achieved a much deeper understanding of computer processing, as well as became more comfortable working with different number bases.

## Important Files

* [LS-8 Specifications](./LS8-spec.md)
* [LS-8 FAQ](./FAQ.md)
* [LS-8 CPU Class](./ls8/cpu.py)
* [CPU Loader](./ls8/ls8.py)
* [LS-8 Programs (Proof of Functionality)](./ls8/examples)
* [ASM to LS-8 Compiler](./asm/asm.py)

## Running Programs on the LS-8

The LS-8 is a console-based computer. When running the loader file, you must make sure you're in the proper directory and that you're passing in a valid program location through the command line.

1. Move  into the `./ls8` directory:

    ``` bash
    cd ls8
    ```

2. Call the loader file and pass in the address to a valid LS-8 program:

    ``` bash
    python ls8 examples/printstr.ls8
    ```

And that's it! Assuming the input file uses the correct LS-8 binary syntax, the program should run as intended.

> **Tip:** Pressing `ESC` at any time will flag the run loop to exit. Useful if you find yourself stuck in any infinite loops!

## Notes About `.ls8` Syntax

`.ls8` files need to follow strict guidelines to run, as the CPU loader is not very "smart".

* Instructions _must_ be written in `8-bit binary` code.
* Only _one_ instruction per line.
* Instructions may be followed by comments, which the loader ignores.
* Blank lines _are_ allowed, and are ignored by the loader.
* Comments may be alone on a line, and are ignored by the loader.
* Comments _must_ begin with `#` , or the loader will throw an error and stop program execution.

## V2 Checklist

These goals, though they may take a large chunk of code to implement, are fairly straightforward and will not require the refactoring of any existing program files:

* [ ] Put the `load()` method call inside the `run()` method, and create a system wherein users can load functions on the fly, and load another function when the first one is done executing
* [x] Move file input processing from `ls8.py` into the CPU `load()` method
* [ ] Refactor ram functions

### Wishlist

These goals will be fairly difficult to implement, and will require the refactoring of any of the example program files that use the `RET` or `CALL` functions:

* [ ] Add parameters to subroutine `CALLs`
* [ ] Add return values to `RET`

## Conclusion

That's all you need to know to begin programming with the LS-8! If you found this program particularly interesting or would like to know more, feel free to reach out to me via [LinkedIn](https://www.linkedin.com/in/brandon-ramirez-b00974b5/).

***Thanks for reading!***
