# LS-8: 8-Bit Computer Emulator V2.0

In this project, we attempted to implement a turing complete emulator of an 8-bit CPU in Python, the pedagogical purpose of the assignment being to understand more deeply how a programming language works. Through the creation of virtual RAM, the use of binary and hexadecimal integers, as well as subroutine CALL and RETURN functions, I definitely achieved a much deeper understanding of computer processing, as well as became more comfortable working with different number bases.

Since achieving the minimum viable product, I have implemented my own changes to make the CPU feel more fun and functional.

## Important Files

* [LS-8 CPU (Main Program!)](./ls8/ls8.py)
* [LS-8 Specifications](./LS8-spec.md)
* [LS-8 FAQ](./FAQ.md)
* [LS-8 Programs (Proof of Functionality)](./ls8/programs)
* [ASM to LS-8 Compiler](./asm/asm.py)

## Running Programs on the LS-8

The LS-8 is a console-based computer. When running the loader file, you must make sure you're in the proper directory in order to ensure that programs can be correctly loaded.

1. Move  into the `./ls8` directory (necessary to read in programs!):

    ``` bash
    cd ls8
    ```

2. Run the `ls8.py` file:

    ``` bash
    python ls8.py
    ```

Now your CPU is up and running! When prompted, enter the name of a valid LS-8 program in the `programs` directory. Errors are handled for nonexistent names, and should not negatively impact the user experience.

If no extension is specified, `.ls8` is automatically appended to the filename you enter. For instance, entering

``` input
>> mult
```

will attempt to load the file

``` input
>> mult.ls8
```

See below for a list of reserved keywords that are the exception to this rule, and should not be used as program names.

### Reserved Keywords

* `exit` will cause the LS-8 to exit (shutdown)
* `list` will print a list of the programs in the `programs` directory
* `help` will print these keywords during runtime

> **Tip:** The `esc` key will flag the program loop to exit, ending any loops. This is particulary useful for the given `interrupts.ls8` and `keyboard.ls8` example programs

## Notes About `.ls8` Syntax

`.ls8` files need to follow strict guidelines to run, as the CPU loader is not very "smart".

* Instructions _must_ be written in `8-bit binary` code.
* Only _one_ instruction per line.
* Instructions may be followed by comments, which the loader ignores.
* Blank lines _are_ allowed, and are ignored by the loader.
* Comments may be alone on a line, and are ignored by the loader.
* Comments _must_ begin with `#` , or the loader will throw an error and stop program execution.

## V2 Checklist

### Implementation Complete

On top of the desired features listed in the below checklist, this version also includes UI improvements and improvements to code readability and modularity.

* [x] Put the `load()` method call inside the `run()` method, and create a system wherein users can load functions on the fly, and load another function when the first one is done executing
* [x] Move file input processing from `ls8.py` into the CPU `load()` method
* [x] Refactor ram functions
* [x] Bonus: remove excess `print` statements and simplify `run()` loop

### V3 Feature Wish List

These goals will be fairly difficult to implement, and will require the refactoring of any of the example program files that use the `RET` or `CALL` functions. They will also cause the compiler and the `cpu.run()` method to require tweaks, and as such may not be appropriate for the desired simplicity of an 8-bit CPU (though they are still very possible).

* [ ] Add parameters to subroutine `CALLs`
* [ ] Add return values to `RET`

## Conclusion

That's all you need to know to begin programming with the LS-8! If you found this program particularly interesting or would like to know more, feel free to reach out to me via [LinkedIn](https://www.linkedin.com/in/brandon-ramirez-b00974b5/).

***Thanks for reading!***
