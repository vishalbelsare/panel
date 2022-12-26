# Using Interact

The `interact` function (`panel.interact`) automatically creates user interface (UI) controls for exploring code and data interactively. It is the easiest way to get started using Panel, and it provides enough flexibility that it may be all you need to learn in Panel.


```{pyodide}
import panel as pn

from panel.interact import interact, fixed
from panel import widgets

pn.extension()
```

## Basic `interact`

At the most basic level, `interact` autogenerates UI controls for function arguments, and then calls the function with those arguments when you manipulate the controls interactively. To use `interact`, you need to define a function that you want to explore. Here is a function that prints its only argument `x`.


```{pyodide}
def f(x):
    return x
```

When you pass this function as the first argument to `interact` along with an integer keyword argument (`x=10`), a slider is generated and bound to the function parameter.


```{pyodide}
interact(f, x=10)
```

When you move the slider, the function is called, which prints the current value of `x`.

If you pass `True` or `False`, `interact` will generate a checkbox:


```{pyodide}
interact(f, x=True)
```

If you pass a string, `interact` will generate a text area.


```{pyodide}
interact(f, x='Hi there!')
```

`interact` can also be used as a decorator. This allows you to define a function and how to interact with it in a single shot. As this example shows, `interact` also works with functions that have multiple arguments.


```{pyodide}
@interact(x=True, y=1.0)
def g(x, y):
    return (x, y)
g
```

## Laying out interact widgets

The ``interact`` function returns a Panel containing the widgets and the display output. By indexing into this Panel we can lay out the objects precisely how we want:


```{pyodide}
layout = interact(f, x=10)

pn.Column('**A custom interact layout**', pn.Row(layout[0], layout[1]))
```

## Fixing arguments using `fixed`

There are times when you may want to explore a function using `interact`, but fix one or more of its arguments to specific values. This can be accomplished by wrapping values with the `fixed` function.


```{pyodide}
def h(p, q):
    return (p, q)
```

When we call `interact`, we pass `fixed(20)` for q to hold it fixed at a value of `20`.

```{pyodide}
interact(h, p=5, q=fixed(20))
```

Notice that a slider is only produced for `p`, as the value of `q` is fixed.

## Widget abbreviations

When you pass an integer-valued keyword argument of `10` (`x=10`) to `interact`, it generates an integer-valued slider control with a range of `[-10,+3*10]`. In this case, `10` is an *abbreviation* for an actual slider widget:

```python
widgets.IntSlider(min=-10,max=30,step=1,value=10)
```

In fact, we can get the same result if we pass this `IntSlider` as the keyword argument for `x`:

```{pyodide}
interact(f, x=widgets.IntSlider(start=-10,end=30,step=1,value=10))
```

This examples clarifies how `interact` proceses its keyword arguments:

1. If the keyword argument is a `Widget` instance with a `value` attribute, that widget is used. Any widget with a `value` attribute can be used, even custom ones.
2. Otherwise, the value is treated as a *widget abbreviation* that is converted to a widget before it is used.

The following table gives an overview of different widget abbreviations:

<table class="table table-condensed table-bordered">
  <tr><td><strong>Keyword argument</strong></td><td><strong>Widget</strong></td></tr>
  <tr><td>True or False</td><td>Checkbox</td></tr>
  <tr><td>'Hi there'</td><td>Text</td></tr>
  <tr><td>value or (min,max,[step,[value]]) if integers are passed</td><td>IntSlider</td></tr>
  <tr><td>value or (min,max,[step,[value]]) if floats are passed</td><td>FloatSlider</td></tr>
  <tr><td>['orange','apple'] or {'one':1,'two':2}</td><td>Dropdown</td></tr>
</table>
Note that a dropdown is used if a list or a dict is given (signifying discrete choices), and a slider is used if a tuple is given (signifying a range).

You have seen how the checkbox and textarea widgets work above. Here, more details about the different abbreviations for sliders and dropdowns are given.

If a 2-tuple of integers is passed `(min,max)`, an integer-valued slider is produced with those minimum and maximum values (inclusively). In this case, the default step size of `1` is used.


```{pyodide}
interact(f, x=(0, 4))
```

If a 3-tuple of integers is passed `(min,max,step)`, the step size can also be set.


```{pyodide}
interact(f, x=(0, 8, 2))
```

A float-valued slider is produced if the elements of the tuples are floats. Here the minimum is `0.0`, the maximum is `10.0` and step size is `0.1` (the default).


```{pyodide}
interact(f, x=(0.0, 10.0))
```

The step size can be changed by passing a third element in the tuple.


```{pyodide}
interact(f, x=(0.0, 10.0, 0.01))
```

For both integer and float-valued sliders, you can pick the initial value of the widget by supplying a default keyword argument when you define the underlying Python function. Here we set the initial value of a float slider to `5.5`.


```{pyodide}
@interact(x=(0.0, 20.0, 0.5))
def h(x=5.5):
    return x

h
```

You can also set the initial value by passing a fourth element in the tuple.


```{pyodide}
interact(f, x=(0.0, 20.0, 0.5, 5.5))
```

Use `None` as the third element to just set min, max, and value.


```{pyodide}
interact(f, x=(0.0, 20.0, None, 5.5))
```

Dropdown menus are constructed by passing a list of strings. In this case, the strings are both used as the names in the dropdown menu UI and passed to the underlying Python function.


```{pyodide}
interact(f, x=['apples', 'oranges'])
```

When working with numeric data ``interact`` will automatically add a discrete slider:


```{pyodide}
interact(f, x=dict([('one', 10), ('two', 20)]))
```

## Disabling continuous updates for slider widgets
When interacting with functions which takes a long time to run, realtime feedback can be a burden instead of being helpful.

If you are using slider widgets and you have a function which takes long time to calculate, you can set the keyword argument `throttled` to `True` in `interact`. This will then first run the function after the release of the mouse button.


```{pyodide}
interact(f, x=(0.0, 20.0, None, 5.5), throttled=True)
```
