# asymptote README

_(This extension is converted from atom language-asymptote package.
It is based on the same grammar. This README is verbatim copied
from the original Atom package.)_

Asymptote is a powerful C-based Vector Graphics Language that can be integrated into LaTeX documents.
The official website of Asymptote is at <http://asymptote.sourceforge.net/>.

## Features

This package mainly highlights asymptote syntax and builtin functions. LSP is currently a work in progress.

## Requirements

For debugging, if one's Asymptote version is < `2.XX`, make sure to apply the debugger patch in `patches/asydbgpatch.patch` by

```sh
cd <path to your asy git repo>
patch <asydbgpatch.patch location> .
sudo make install
```

## Known Issues

For now, I am not able to have the extension match the string grammar to LaTeX. This should be fixed soon... See <http://asymptote.sourceforge.net/doc/Data-types.html> on "string" section.

## Contributors

Apart from me, John Bowman helped with Asymptote keywords and grammar generation.

## Special Thanks

John Bowman, Andy Hammerlindl and Tom Prince, and other students for development of the original Asymptote language. The full credits can be seen at http://asymptote.sourceforge.net/.

## License

Copyright (c) 2017-2025 Supakorn Rassameemasmuang See LICENSE.md for more details.

This project uses derivative code built from Asymptote, which can be retrieved under https://github.com/vectorgraphics/asymptote.