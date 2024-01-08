# README for Magic-Carpet Python Package

## Overview

Magic-Carpet is a versatile Python package that enables users to easily manage and deploy multiple model endpoints. It is designed to streamline the process of handling various machine learning models by providing a unified interface. With Magic-Carpet, users can create a customized router to dynamically choose which model to use based on the input, allowing for more efficient and targeted model inference.

## Features

- **Multiple Model Management**: Easily spin up and manage multiple model endpoints using the `NamedModel` class.
- **Customized Routing**: Design a customized router to decide per-input which model endpoint to hit.
- **Dynamic Model Selection**: Dynamically route requests to different models based on the input data.
- **Ease of Integration**: Simple integration with existing Python applications and machine learning workflows.
- **Extensive Documentation**: Includes detailed examples and use cases in `examples/`.

## Installation

To install Magic-Carpet, simply run:

```bash
pip install magic-carpet
```

## Usage

### Setting Up Models

Use the `NamedModel` class to define and spin up your model endpoints:

```python
from magic_carpet import NamedModel

# Define models
foo = NamedModel(name="foo", function=lambda x: x + 1)
bar = NamedModel(name="bar", function=lambda y: 2 * y)

print(foo(1), bar(2))     # 2, 4
```

### Customizing the Router

Subclass the `NamedRouter` class to create a customized router for dynamic model selection:

```python
from magic_carpet import NamedRouter

class CustomRouter(NamedRouter):
    def route(self, input, custom_arg):
        # Implement logic to choose model based on input_data
        if (custom_arg is not None) and input > 0:
            return self.models["foo"]
        return self.models["bar"]

# Initialize the router
foobar_router = CustomRouter([foo, bar])
```

### Running the Router

The router itself is an instance of `NamedModel` and thus can be called just like you would a `NamedModel`
```python
# Process an input
print(foobar_router(5, custom_arg="hello"), foobar_router(-1))    # 6, -2
```

### Running Evaluations
We also provide util functions to test out multiple models over various evalaution functions. To learn more about this please refer to `examples/testing/example.ipynb`.

## Examples

For a comprehensive guide and examples on how to use Magic-Carpet, please refer to the Jupyter notebooks in `examples/` included in the package. These notebook provides more detailed instructions and use-cases for using this package.

## Support

For issues, questions, or contributions, please refer to the GitHub repository: [Magic-Carpet GitHub](https://github.com/loral-labs/magic-carpet).

## License

Magic-Carpet is released under the MIT License. See the LICENSE file for more details.