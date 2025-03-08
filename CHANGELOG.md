# Change Log

## [2.X.X]

- Changed how string syntax highlighting works. Now, `""` will be treated as a regular string. To enable latex
  highlighting, enclose the string in a `_tex` wrapper function, like

  ```asymptote
  string s = _tex("$\int_B f < I>");
  ```

  If `_tex` is not defined in asymptote, you can define it manually by

  ```asymptote
  string _tex(string s)
  {
    return s;
  }
  ```

  Fixes [issues/7](https://github.com/vectorgraphics/vscode-lang-asymptote/issues/7).

## [2.0.0]

- Add support for LSP mode (work in progress).
- Update definitions file to support Asymptote 3.01.

## [Unreleased]

- Initial release
