# DecMore

> This library contains some decorators that will be useful for both daily development and application needs.

## Decorators

### CheckTypes:
_This decorator checks if the types of the variables sent are the same as the ones the function needs_
<br>
<br>
Example:

```python
from decmore import CheckTypes


@CheckTypes
def func(var1: str, var2: list, var3: list | tuple):
    ...


if __name__ == "__main__":
    func(1, [], var3=None)

    """ The execution will return a TypeError like this
    
    TypeError: 
    Param 'var1' Expected <class 'str'>, got <class 'int'> instead
    Param 'var3' Expected <class 'list'> or <class 'tuple'>, got <class 'NoneType'> instead
    
    """

```

### Profiler:
_This decorator shows how long each line of your function took to execute_
<br>
<br>
Example:

```python
from time import sleep
from decmore import Profiler


@Profiler()
def func():
    sleep(10)


if __name__ == "__main__":
    func()

    """ The execution will show the data on the console like this
    
     3 function calls in 10.009 seconds
  
     Ordered by: internal time
  
     ncalls  tottime  percall  cumtime  percall filename:lineno(function)
          1   10.009   10.009   10.009   10.009 {built-in method time.sleep}
          1    0.000    0.000   10.009   10.009 main.py:4(func)
          1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
    """

```
## Authors
> Daniel Relvas Trivelli
> <br>
>  * <a href="https://github.com/DanielTrivelli" target="_blank" rel="noopener noreferrer">GitHub<a/>
>  * <a href="https://www.linkedin.com/in/daniel-relvas-trivelli/" target="_blank" rel="noopener noreferrer">LinkedIn<a/>

## License
This project is under the MIT license. See the file [LICENSE](LICENSE.md) for more details.
