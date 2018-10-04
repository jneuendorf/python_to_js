# python_to_js

Yet another python to JavaScript transpiler.

I wanted to play around with ASTs and `babel` and wanted some pythonic languages features in JS.

The main features I want is _keyword arguments_.
Since it is currently impossible to add new AST node types to `babylon` without forking it, I figured I could just use python's built-in `ast` module to generate and modify an AST that `babel` can handle.

The idea is to have frontend code that _looks_ like python.
It does not mean that the entire standard library is also being implemented (like [brython](https://github.com/brython-dev/brython)) or that the resulting behavior is identical.

For example, `dict()` or `{}` creates a JavaScript `Object` which behaves differently that `dict`.
Another example is that `func.__name__` will be `undefined` whereas `func.name` won't.
Those kinds of features may be implemented as runtime features in the future.


## Testing / Development

### The python part

```bash
yarn test:python
```

### The entire process

```bash
yarn test
```

## Caveats

To be begun...
