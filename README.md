# cykubed-common

This project is intended to be included as a git submodule to the [cykubed-runner](https://github.com/cykubed/cykubed-runner) and [cykubed-agent](https://github.com/cykubed/cykubed-agent) projects. It contains the Pydantic schemas for all Cykubed data models used by the [Cykubed API](https://api.cykubed.com/redoc), along with a small collection of common utilities.

## Python bindings

* _schemas.py_ : all [Pydantic 1.x](https://docs.pydantic.dev/1.10/) data models
* _enums.py_ : all  [Pydantic 1.x](https://docs.pydantic.dev/1.10/) enums


## Typescript bindings

You can easily generate Typescript types and interfaces from the Pydantic schema using [pydantic-to-typescript](https://pypi.org/project/pydantic-to-typescript/): 

```pydantic2ts --module schemas --output generated.model.ts```
